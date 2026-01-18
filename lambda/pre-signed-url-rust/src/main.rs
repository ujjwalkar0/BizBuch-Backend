use aws_config::BehaviorVersion;
use aws_sdk_s3::presigning::PresigningConfig;
use aws_sdk_s3::Client as S3Client;
use lambda_runtime::{service_fn, Error, LambdaEvent};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;
use std::time::Duration;
use jsonwebtoken::{decode, Algorithm, DecodingKey, Validation};
use uuid::Uuid;

// Request/Response types
#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct PresignUploadRequest {
    content_type: String,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct PresignUploadResponse {
    upload_url: String,
    public_url: String,
}

#[derive(Deserialize)]
struct PresignViewRequest {
    key: String,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct PresignViewResponse {
    view_url: String,
}

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

// API Gateway request/response
#[derive(Deserialize)]
struct ApiGatewayRequest {
    path: String,
    #[serde(rename = "httpMethod")]
    http_method: String,
    headers: Option<HashMap<String, String>>,
    body: Option<String>,
}

#[derive(Serialize)]
struct ApiGatewayResponse {
    #[serde(rename = "statusCode")]
    status_code: u16,
    headers: HashMap<String, String>,
    body: String,
}

// JWT Claims - matches Django SimpleJWT
#[derive(Debug, Deserialize)]
struct JwtClaims {
    user_id: i64,
    token_type: String,
    exp: usize,
}

// Allowed origins for CORS
const ALLOWED_ORIGINS: &[&str] = &[
    "http://localhost:3000",
    "http://localhost:8080",
    "https://startupoverflowweb.netlify.app",
];

const ALLOWED_CONTENT_TYPES: &[&str] = &["image/jpeg", "image/png", "image/webp"];

#[tokio::main]
async fn main() -> Result<(), Error> {
    lambda_runtime::run(service_fn(handler)).await
}

async fn handler(event: LambdaEvent<ApiGatewayRequest>) -> Result<ApiGatewayResponse, Error> {
    let (request, _context) = event.into_parts();
    
    // Get CORS headers
    let origin = request.headers
        .as_ref()
        .and_then(|h| h.get("origin").or_else(|| h.get("Origin")))
        .map(|s| s.as_str())
        .unwrap_or("");
    
    let mut headers = get_cors_headers(origin);

    // Handle preflight OPTIONS request
    if request.http_method == "OPTIONS" {
        return Ok(ApiGatewayResponse {
            status_code: 200,
            headers,
            body: String::new(),
        });
    }

    // Initialize AWS SDK
    let config = aws_config::load_defaults(BehaviorVersion::latest()).await;
    let s3_client = S3Client::new(&config);
    
    let bucket = env::var("AWS_S3_BUCKET").unwrap_or_else(|_| "bizbuch-media".to_string());
    let jwt_secret = env::var("JWT_SECRET").unwrap_or_default();

    // Route based on path
    match request.path.as_str() {
        "/presign/upload" => {
            handle_presign_upload(&request, &s3_client, &bucket, &jwt_secret, &mut headers).await
        }
        "/presign/view" => {
            handle_presign_view(&request, &s3_client, &bucket, &jwt_secret, &mut headers).await
        }
        _ => Ok(json_response(404, &ErrorResponse { error: "Not found".to_string() }, headers)),
    }
}

async fn handle_presign_upload(
    request: &ApiGatewayRequest,
    s3_client: &S3Client,
    bucket: &str,
    jwt_secret: &str,
    headers: &mut HashMap<String, String>,
) -> Result<ApiGatewayResponse, Error> {
    // Validate JWT
    let user_id = match validate_jwt(request, jwt_secret) {
        Ok(id) => id,
        Err(e) => return Ok(json_response(401, &ErrorResponse { error: e }, headers.clone())),
    };

    // Parse request body
    let body = match &request.body {
        Some(b) => b,
        None => return Ok(json_response(400, &ErrorResponse { error: "Missing request body".to_string() }, headers.clone())),
    };

    let req: PresignUploadRequest = match serde_json::from_str(body) {
        Ok(r) => r,
        Err(_) => return Ok(json_response(400, &ErrorResponse { error: "Invalid request body".to_string() }, headers.clone())),
    };

    // Validate content type
    if !ALLOWED_CONTENT_TYPES.contains(&req.content_type.as_str()) {
        return Ok(json_response(400, &ErrorResponse { 
            error: "Unsupported file type. Allowed: image/jpeg, image/png, image/webp".to_string() 
        }, headers.clone()));
    }

    // Generate unique key
    let key = format!("posts/{}/{}.jpg", user_id, Uuid::new_v4());

    // Generate presigned upload URL (5 minutes)
    let presign_config = PresigningConfig::builder()
        .expires_in(Duration::from_secs(300))
        .build()
        .unwrap();

    let presigned = s3_client
        .put_object()
        .bucket(bucket)
        .key(&key)
        .content_type(&req.content_type)
        .presigned(presign_config)
        .await;

    match presigned {
        Ok(presigned_req) => {
            let response = PresignUploadResponse {
                upload_url: presigned_req.uri().to_string(),
                public_url: key,
            };
            Ok(json_response(200, &response, headers.clone()))
        }
        Err(_) => Ok(json_response(500, &ErrorResponse { 
            error: "Failed to generate presigned URL".to_string() 
        }, headers.clone())),
    }
}

async fn handle_presign_view(
    request: &ApiGatewayRequest,
    s3_client: &S3Client,
    bucket: &str,
    jwt_secret: &str,
    headers: &mut HashMap<String, String>,
) -> Result<ApiGatewayResponse, Error> {
    // Validate JWT
    if let Err(e) = validate_jwt(request, jwt_secret) {
        return Ok(json_response(401, &ErrorResponse { error: e }, headers.clone()));
    }

    // Parse request body
    let body = match &request.body {
        Some(b) => b,
        None => return Ok(json_response(400, &ErrorResponse { error: "Missing request body".to_string() }, headers.clone())),
    };

    let req: PresignViewRequest = match serde_json::from_str(body) {
        Ok(r) => r,
        Err(_) => return Ok(json_response(400, &ErrorResponse { error: "Invalid request body".to_string() }, headers.clone())),
    };

    if req.key.is_empty() {
        return Ok(json_response(400, &ErrorResponse { error: "Key is required".to_string() }, headers.clone()));
    }

    // Generate presigned view URL (1 hour)
    let presign_config = PresigningConfig::builder()
        .expires_in(Duration::from_secs(3600))
        .build()
        .unwrap();

    let presigned = s3_client
        .get_object()
        .bucket(bucket)
        .key(&req.key)
        .presigned(presign_config)
        .await;

    match presigned {
        Ok(presigned_req) => {
            let response = PresignViewResponse {
                view_url: presigned_req.uri().to_string(),
            };
            Ok(json_response(200, &response, headers.clone()))
        }
        Err(_) => Ok(json_response(500, &ErrorResponse { 
            error: "Failed to generate presigned URL".to_string() 
        }, headers.clone())),
    }
}

fn validate_jwt(request: &ApiGatewayRequest, jwt_secret: &str) -> Result<i64, String> {
    let headers = request.headers.as_ref().ok_or("Missing headers")?;
    
    let auth_header = headers
        .get("Authorization")
        .or_else(|| headers.get("authorization"))
        .ok_or("Missing authorization header")?;

    if !auth_header.starts_with("Bearer ") {
        return Err("Invalid authorization header format".to_string());
    }

    let token = &auth_header[7..];

    let validation = Validation::new(Algorithm::HS256);
    let token_data = decode::<JwtClaims>(
        token,
        &DecodingKey::from_secret(jwt_secret.as_bytes()),
        &validation,
    ).map_err(|e| format!("Invalid token: {}", e))?;

    // Verify it's an access token
    if token_data.claims.token_type != "access" {
        return Err("Invalid token type".to_string());
    }

    Ok(token_data.claims.user_id)
}

fn get_cors_headers(origin: &str) -> HashMap<String, String> {
    let allowed_origin = if ALLOWED_ORIGINS.contains(&origin) {
        origin.to_string()
    } else {
        String::new()
    };

    let mut headers = HashMap::new();
    headers.insert("Content-Type".to_string(), "application/json".to_string());
    headers.insert("Access-Control-Allow-Origin".to_string(), allowed_origin);
    headers.insert("Access-Control-Allow-Methods".to_string(), "POST, OPTIONS".to_string());
    headers.insert("Access-Control-Allow-Headers".to_string(), "Content-Type, Authorization".to_string());
    headers
}

fn json_response<T: Serialize>(status_code: u16, body: &T, headers: HashMap<String, String>) -> ApiGatewayResponse {
    ApiGatewayResponse {
        status_code,
        headers,
        body: serde_json::to_string(body).unwrap_or_else(|_| r#"{"error":"Internal server error"}"#.to_string()),
    }
}
