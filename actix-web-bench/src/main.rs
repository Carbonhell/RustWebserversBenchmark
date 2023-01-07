use actix_web::{get, App, HttpResponse, HttpServer, Responder};
use actix_files;
use actix_web::web::Query;
use serde::Deserialize;
use std::env;
use actix_web::middleware::{Compress, Condition};

#[derive(Deserialize)]
struct Info {
    first: u32,
    second: u32,
}

#[get("/dynamic")]
async fn sum(info: Query<Info>) -> impl Responder {
    HttpResponse::Ok()
        .body(format!("The sum of {} and {} is: {}", info.first, info.second, info.first + info.second))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let compression_enabled = env::args().any(|x| x == "--compression" || x == "-c");
    if compression_enabled {
        println!("Compression enabled.");
    }
    let single_threaded = env::args().any(|x| x == "--single-thread" || x == "-s");
    if single_threaded {
        println!("Running in single threaded mode.");
    }

    let mut server = HttpServer::new(move || {
        App::new()
            .wrap(Condition::new(
                compression_enabled,
                Compress::default(),
            ))
            .service(sum)
            .service(actix_files::Files::new("/", "../static"))
    })
        .bind(("0.0.0.0", 8080))?;

    if single_threaded {
        server = server.workers(1);
    }
    server
        .run()
        .await
}