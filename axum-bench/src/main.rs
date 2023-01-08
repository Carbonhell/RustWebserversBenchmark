use std::io;
use axum::{
    routing::get,
    Router,
};
use axum::extract::Query;
use axum::http::{StatusCode};
use axum::response::IntoResponse;
use axum::routing::get_service;
use tower_http::services::ServeDir;
use serde::Deserialize;
#[cfg(feature = "compression")]
use {
    tower::ServiceBuilder,
    tower_http::compression::CompressionLayer
};

#[derive(Deserialize)]
struct Info {
    first: u32,
    second: u32,
}

async fn handler(Query(info): Query<Info>) -> String {
    format!("The sum of {} and {} is: {}", info.
        first, info.second, info.first + info.second)
}

#[cfg(feature = "compression")]
fn setup_compression(router: Router) -> Router {
    router.layer(ServiceBuilder::new().layer(CompressionLayer::new()))
}

#[cfg(not(feature = "compression"))]
fn setup_compression(router: Router) -> Router {
    router
}

#[cfg_attr(not(feature = "single_threaded"), tokio::main)]
#[cfg_attr(feature = "single_threaded", tokio::main(flavor = "current_thread"))]
async fn main() {
    let static_file_service = get_service(ServeDir::new("../static"))
        .handle_error(handle_error);

    let mut app = Router::new()
        .route("/dynamic", get(handler))
        .fallback_service(static_file_service);

    app = setup_compression(app);

    axum::Server::bind(&"0.0.0.0:8080".parse().unwrap())
        .serve(app.into_make_service())
        .await
        .unwrap();
}

async fn handle_error(_err: io::Error) -> impl IntoResponse {
    (StatusCode::INTERNAL_SERVER_ERROR, "Something went wrong...")
}
