package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"sync"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/credentials"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
)

var (
	s3Client       *s3.Client
	presignClient  *s3.PresignClient
	bucketName     string
	jwtSecret      string
	rateLimiter    *RateLimiter
	allowedOrigins = []string{
		"http://localhost:3000",
		"http://localhost:8080",
	}
)

// RateLimiter - Token bucket rate limiter per user
type RateLimiter struct {
	mu       sync.Mutex
	users    map[int64]*userBucket
	rate     int           // requests per window
	window   time.Duration // time window
	cleanup  time.Duration // cleanup interval
}

type userBucket struct {
	tokens    int
	lastReset time.Time
}

func NewRateLimiter(rate int, window time.Duration) *RateLimiter {
	rl := &RateLimiter{
		users:  make(map[int64]*userBucket),
		rate:   rate,
		window: window,
	}
	// Cleanup old entries every 5 minutes
	go rl.cleanupLoop(5 * time.Minute)
	return rl
}

func (rl *RateLimiter) Allow(userID int64) bool {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	now := time.Now()
	bucket, exists := rl.users[userID]

	if !exists || now.Sub(bucket.lastReset) >= rl.window {
		// Reset bucket
		rl.users[userID] = &userBucket{
			tokens:    rl.rate - 1,
			lastReset: now,
		}
		return true
	}

	if bucket.tokens > 0 {
		bucket.tokens--
		return true
	}

	return false
}

func (rl *RateLimiter) cleanupLoop(interval time.Duration) {
	for {
		time.Sleep(interval)
		rl.mu.Lock()
		now := time.Now()
		for userID, bucket := range rl.users {
			if now.Sub(bucket.lastReset) > rl.window*2 {
				delete(rl.users, userID)
			}
		}
		rl.mu.Unlock()
	}
}

// Request/Response types
type PresignUploadRequest struct {
	ContentType string `json:"contentType"`
}

type PresignUploadResponse struct {
	UploadURL string `json:"uploadUrl"`
	PublicURL string `json:"publicUrl"`
}

type PresignViewRequest struct {
	Key string `json:"key"`
}

type PresignViewResponse struct {
	ViewURL string `json:"viewUrl"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

// JWT Claims - matches Django SimpleJWT token structure
type JWTClaims struct {
	UserID    int64  `json:"user_id"`
	TokenType string `json:"token_type"` // "access" or "refresh"
	jwt.RegisteredClaims
}

func init() {
	bucketName = os.Getenv("AWS_S3_BUCKET")
	if bucketName == "" {
		bucketName = "bizbuch-media"
	}

	jwtSecret = os.Getenv("JWT_SECRET")
	if jwtSecret == "" {
		jwtSecret = "dev-secret-key"
	}

	region := os.Getenv("AWS_REGION")
	if region == "" {
		region = "ap-south-1"
	}

	// Initialize AWS SDK with explicit credentials for local dev
	var cfg aws.Config
	var err error

	accessKey := os.Getenv("AWS_ACCESS_KEY_ID")
	secretKey := os.Getenv("AWS_SECRET_ACCESS_KEY")

	if accessKey != "" && secretKey != "" {
		cfg, err = config.LoadDefaultConfig(context.TODO(),
			config.WithRegion(region),
			config.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(accessKey, secretKey, "")),
		)
	} else {
		cfg, err = config.LoadDefaultConfig(context.TODO(),
			config.WithRegion(region),
		)
	}

	if err != nil {
		log.Fatalf("Unable to load SDK config: %v", err)
	}

	s3Client = s3.NewFromConfig(cfg)
	presignClient = s3.NewPresignClient(s3Client)

	// Initialize rate limiter: 10 requests per minute per user
	rateLimiter = NewRateLimiter(10, time.Minute)
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8081"
	}

	http.HandleFunc("/presign/upload", corsMiddleware(rateLimitMiddleware(handlePresignUpload)))
	http.HandleFunc("/presign/view", corsMiddleware(rateLimitMiddleware(handlePresignView)))
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("OK"))
	})

	log.Printf("Server starting on http://localhost:%s", port)
	log.Printf("Endpoints:")
	log.Printf("  POST /presign/upload")
	log.Printf("  POST /presign/view")
	log.Printf("  GET  /health")
	log.Printf("Rate limit: 10 requests/minute per user")

	log.Fatal(http.ListenAndServe(":"+port, nil))
}

// rateLimitMiddleware checks rate limit after JWT validation
func rateLimitMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// Extract user ID from JWT for rate limiting
		userID, err := validateJWTAndGetUserID(r)
		if err != nil {
			jsonError(w, err.Error(), http.StatusUnauthorized)
			return
		}

		if !rateLimiter.Allow(userID) {
			w.Header().Set("Retry-After", "60")
			jsonError(w, "Rate limit exceeded. Try again later.", http.StatusTooManyRequests)
			return
		}

		// Store userID in context to avoid re-validating JWT
		ctx := context.WithValue(r.Context(), "userID", userID)
		next(w, r.WithContext(ctx))
	}
}

func corsMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		origin := r.Header.Get("Origin")
		for _, allowed := range allowedOrigins {
			if origin == allowed {
				w.Header().Set("Access-Control-Allow-Origin", origin)
				break
			}
		}
		w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		w.Header().Set("Content-Type", "application/json")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next(w, r)
	}
}

func handlePresignUpload(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		jsonError(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Get userID from context (set by rateLimitMiddleware)
	userID := r.Context().Value("userID").(int64)

	var req PresignUploadRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		jsonError(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if !isAllowedContentType(req.ContentType) {
		jsonError(w, "Unsupported file type. Allowed: image/jpeg, image/png, image/webp", http.StatusBadRequest)
		return
	}

	key := fmt.Sprintf("posts/%d/%s.jpg", userID, uuid.New().String())

	presignReq, err := presignClient.PresignPutObject(context.TODO(), &s3.PutObjectInput{
		Bucket:      aws.String(bucketName),
		Key:         aws.String(key),
		ContentType: aws.String(req.ContentType),
	}, s3.WithPresignExpires(5*time.Minute))

	if err != nil {
		jsonError(w, "Failed to generate presigned URL", http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(PresignUploadResponse{
		UploadURL: presignReq.URL,
		PublicURL: key,
	})
}

func handlePresignView(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		jsonError(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// userID already validated by rateLimitMiddleware

	var req PresignViewRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		jsonError(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	if req.Key == "" {
		jsonError(w, "Key is required", http.StatusBadRequest)
		return
	}

	presignReq, err := presignClient.PresignGetObject(context.TODO(), &s3.GetObjectInput{
		Bucket: aws.String(bucketName),
		Key:    aws.String(req.Key),
	}, s3.WithPresignExpires(1*time.Hour))

	if err != nil {
		jsonError(w, "Failed to generate presigned URL", http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(PresignViewResponse{
		ViewURL: presignReq.URL,
	})
}

func validateJWTAndGetUserID(r *http.Request) (int64, error) {
	authHeader := r.Header.Get("Authorization")
	if authHeader == "" {
		return 0, fmt.Errorf("missing authorization header")
	}

	if len(authHeader) < 7 || authHeader[:7] != "Bearer " {
		return 0, fmt.Errorf("invalid authorization header format")
	}

	tokenString := authHeader[7:]

	token, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (interface{}, error) {
		// Django SimpleJWT uses HS256 by default
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return []byte(jwtSecret), nil
	})

	if err != nil {
		return 0, fmt.Errorf("invalid token: %v", err)
	}

	claims, ok := token.Claims.(*JWTClaims)
	if !ok || !token.Valid {
		return 0, fmt.Errorf("invalid token claims")
	}

	// Verify it's an access token, not a refresh token
	if claims.TokenType != "access" {
		return 0, fmt.Errorf("invalid token type")
	}

	return claims.UserID, nil
}

func isAllowedContentType(contentType string) bool {
	allowedTypes := []string{"image/jpeg", "image/png", "image/webp"}
	for _, allowed := range allowedTypes {
		if contentType == allowed {
			return true
		}
	}
	return false
}

func jsonError(w http.ResponseWriter, message string, statusCode int) {
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(ErrorResponse{Error: message})
}
