use axum::{
    extract::Path,
    http::StatusCode,
    response::Json,
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};

#[derive(Clone, Serialize, Deserialize)]
struct User {
    id: u64,
    username: String,
    email: String,
}

#[derive(Deserialize)]
struct UserCreate {
    username: String,
    email: String,
}

type UsersDb = Arc<Mutex<Vec<User>>>;

async fn root() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "status": "ok",
        "message": "QuinotoSpec Example API"
    }))
}

async fn list_users(axum::extract::State(db): axum::extract::State<UsersDb>) -> Json<Vec<User>> {
    Json(db.lock().unwrap().clone())
}

async fn create_user(
    axum::extract::State(db): axum::extract::State<UsersDb>,
    Json(payload): Json<UserCreate>,
) -> (StatusCode, Json<User>) {
    let mut users = db.lock().unwrap();
    let next_id = users.len() as u64 + 1;
    let user = User {
        id: next_id,
        username: payload.username,
        email: payload.email,
    };
    users.push(user.clone());
    (StatusCode::CREATED, Json(user))
}

async fn get_user(
    axum::extract::State(db): axum::extract::State<UsersDb>,
    Path(user_id): Path<u64>,
) -> Result<Json<User>, StatusCode> {
    let users = db.lock().unwrap();
    users
        .iter()
        .find(|u| u.id == user_id)
        .cloned()
        .map(Json)
        .ok_or(StatusCode::NOT_FOUND)
}

#[tokio::main]
async fn main() {
    let db: UsersDb = Arc::new(Mutex::new(Vec::new()));
    let app = build_router(db);

    let addr = std::net::SocketAddr::from(([127, 0, 0, 1], 3000));
    println!("QuinotoSpec Example API listening on {addr}");
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

fn build_router(db: UsersDb) -> Router {
    Router::new()
        .route("/", get(root))
        .route("/users", get(list_users).post(create_user))
        .route("/users/:id", get(get_user))
        .with_state(db)
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::body::Body;
    use axum::http::{Request, StatusCode};
    use tower::ServiceExt;

    fn test_app() -> Router {
        build_router(Arc::new(Mutex::new(Vec::new())))
    }

    #[tokio::test]
    async fn test_root() {
        let res = test_app()
            .oneshot(Request::builder().uri("/").body(Body::empty()).unwrap())
            .await
            .unwrap();
        assert_eq!(res.status(), StatusCode::OK);
    }

    #[tokio::test]
    async fn test_create_and_get_user() {
        let app = test_app();
        let req = Request::builder()
            .method("POST")
            .uri("/users")
            .header("content-type", "application/json")
            .body(Body::from(
                r#"{"username": "testuser", "email": "test@example.com"}"#,
            ))
            .unwrap();
        let res = app.clone().oneshot(req).await.unwrap();
        assert_eq!(res.status(), StatusCode::CREATED);

        let req = Request::builder().uri("/users/1").body(Body::empty()).unwrap();
        let res = app.oneshot(req).await.unwrap();
        assert_eq!(res.status(), StatusCode::OK);
    }
}
