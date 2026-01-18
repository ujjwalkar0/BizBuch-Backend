package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
)

var (
	s3Client       *s3.Client
	presignClient  *s3.PresignClient
	bucketName     string
	jwtSecret      string
	allowedOrigins = []string{
		"http://localhost:3000",
		"http://localhost:8080",
	}
)

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

// FlexibleInt64 handles both string and number JSON values for user_id
type FlexibleInt64 int64

func (f *FlexibleInt64) UnmarshalJSON(data []byte) error {
	// Try to unmarshal as int64 first
	var intVal int64
	if err := json.Unmarshal(data, &intVal); err == nil {
		*f = FlexibleInt64(intVal)
		return nil
	}

	// Try to unmarshal as string and convert
	var strVal string
	if err := json.Unmarshal(data, &strVal); err == nil {
		parsed, err := strconv.ParseInt(strVal, 10, 64)
		if err != nil {
			return fmt.Errorf("cannot parse user_id string '%s' as int64: %v", strVal, err)
		}
		*f = FlexibleInt64(parsed)
		return nil
	}

	return fmt.Errorf("user_id must be a number or numeric string")
}

// JWT Claims - matches Django SimpleJWT token structure
type JWTClaims struct {
	UserID    FlexibleInt64 `json:"user_id"`
	TokenType string        `json:"token_type"` // "access" or "refresh"
	jwt.RegisteredClaims
}

func init() {
	// Load environment variables
	bucketName = os.Getenv("AWS_S3_BUCKET")
	if bucketName == "" {
		bucketName = "bizbuch-media"
	}

	jwtSecret = os.Getenv("JWT_SECRET")

	// Initialize AWS SDK
	cfg, err := config.LoadDefaultConfig(context.TODO(),
		config.WithRegion(os.Getenv("AWS_REGION")),
	)
	if err != nil {
		panic(fmt.Sprintf("unable to load SDK config: %v", err))
	}

	s3Client = s3.NewFromConfig(cfg)
	presignClient = s3.NewPresignClient(s3Client)
}

func main() {
	lambda.Start(handler)
}

func handler(ctx context.Context, request events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	// Set CORS headers
	headers := getCORSHeaders(request.Headers["origin"])

	// Handle preflight OPTIONS request
	if request.HTTPMethod == "OPTIONS" {
		return events.APIGatewayProxyResponse{
			StatusCode: http.StatusOK,
			Headers:    headers,
		}, nil
	}

	// Route based on path
	switch request.Path {
	case "/presign/upload":
		return handlePresignUpload(ctx, request, headers)
	case "/presign/view":
		return handlePresignView(ctx, request, headers)
	default:
		return jsonResponse(http.StatusNotFound, ErrorResponse{Error: "Not found"}, headers)
	}
}

func handlePresignUpload(ctx context.Context, request events.APIGatewayProxyRequest, headers map[string]string) (events.APIGatewayProxyResponse, error) {
	// Validate JWT and extract user ID
	userID, err := validateJWTAndGetUserID(request.Headers)
	if err != nil {
		return jsonResponse(http.StatusUnauthorized, ErrorResponse{Error: err.Error()}, headers)
	}

	// Parse request body
	var req PresignUploadRequest
	if err := json.Unmarshal([]byte(request.Body), &req); err != nil {
		return jsonResponse(http.StatusBadRequest, ErrorResponse{Error: "Invalid request body"}, headers)
	}

	// Validate content type
	if !isAllowedContentType(req.ContentType) {
		return jsonResponse(http.StatusBadRequest, ErrorResponse{Error: "Unsupported file type. Allowed: image/jpeg, image/png, image/webp"}, headers)
	}

	// Generate unique key
	key := fmt.Sprintf("posts/%d/%s.jpg", userID, uuid.New().String())

	// Generate presigned upload URL (expires in 5 minutes)
	presignReq, err := presignClient.PresignPutObject(ctx, &s3.PutObjectInput{
		Bucket:      aws.String(bucketName),
		Key:         aws.String(key),
		ContentType: aws.String(req.ContentType),
	}, s3.WithPresignExpires(5*time.Minute))

	if err != nil {
		return jsonResponse(http.StatusInternalServerError, ErrorResponse{Error: "Failed to generate presigned URL"}, headers)
	}

	response := PresignUploadResponse{
		UploadURL: presignReq.URL,
		PublicURL: key, // Return the key, frontend can construct full URL if needed
	}

	return jsonResponse(http.StatusOK, response, headers)
}

func handlePresignView(ctx context.Context, request events.APIGatewayProxyRequest, headers map[string]string) (events.APIGatewayProxyResponse, error) {
	// Validate JWT
	_, err := validateJWTAndGetUserID(request.Headers)
	if err != nil {
		return jsonResponse(http.StatusUnauthorized, ErrorResponse{Error: err.Error()}, headers)
	}

	// Parse request body
	var req PresignViewRequest
	if err := json.Unmarshal([]byte(request.Body), &req); err != nil {
		return jsonResponse(http.StatusBadRequest, ErrorResponse{Error: "Invalid request body"}, headers)
	}

	if req.Key == "" {
		return jsonResponse(http.StatusBadRequest, ErrorResponse{Error: "Key is required"}, headers)
	}

	// Generate presigned view URL (expires in 1 hour)
	presignReq, err := presignClient.PresignGetObject(ctx, &s3.GetObjectInput{
		Bucket: aws.String(bucketName),
		Key:    aws.String(req.Key),
	}, s3.WithPresignExpires(1*time.Hour))

	if err != nil {
		return jsonResponse(http.StatusInternalServerError, ErrorResponse{Error: "Failed to generate presigned URL"}, headers)
	}

	response := PresignViewResponse{
		ViewURL: presignReq.URL,
	}

	return jsonResponse(http.StatusOK, response, headers)
}

func validateJWTAndGetUserID(headers map[string]string) (int64, error) {
	// Get Authorization header (case-insensitive)
	authHeader := headers["Authorization"]
	if authHeader == "" {
		authHeader = headers["authorization"]
	}

	if authHeader == "" {
		return 0, fmt.Errorf("missing authorization header")
	}

	// Extract token from "Bearer <token>"
	if len(authHeader) < 7 || authHeader[:7] != "Bearer " {
		return 0, fmt.Errorf("invalid authorization header format")
	}

	tokenString := authHeader[7:]

	// Parse and validate JWT
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

	return int64(claims.UserID), nil
}

func isAllowedContentType(contentType string) bool {
	allowedTypes := []string{
		"image/jpeg",
		"image/png",
		"image/webp",
	}

	for _, allowed := range allowedTypes {
		if contentType == allowed {
			return true
		}
	}
	return false
}

func getCORSHeaders(origin string) map[string]string {
	allowedOrigin := ""
	for _, allowed := range allowedOrigins {
		if origin == allowed {
			allowedOrigin = origin
			break
		}
	}

	return map[string]string{
		"Content-Type":                 "application/json",
		"Access-Control-Allow-Origin":  allowedOrigin,
		"Access-Control-Allow-Methods": "POST, OPTIONS",
		"Access-Control-Allow-Headers": "Content-Type, Authorization",
	}
}

func jsonResponse(statusCode int, body interface{}, headers map[string]string) (events.APIGatewayProxyResponse, error) {
	jsonBody, err := json.Marshal(body)
	if err != nil {
		return events.APIGatewayProxyResponse{
			StatusCode: http.StatusInternalServerError,
			Headers:    headers,
			Body:       `{"error": "Internal server error"}`,
		}, nil
	}

	return events.APIGatewayProxyResponse{
		StatusCode: statusCode,
		Headers:    headers,
		Body:       string(jsonBody),
	}, nil
}
