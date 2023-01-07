use rocket::fs::FileServer;
use rocket::{Build, Rocket, routes, get};

#[cfg(feature = "compression")]
use rocket_async_compression::Compression;


#[get("/dynamic?<first>&<second>")]
fn sum(first: u32, second: u32) -> String {
    format!("The sum of {} and {} is: {}",
            first, second, first + second)
}

#[cfg(feature = "compression")]
fn setup_compression(rocket: Rocket<Build>) -> Rocket<Build> {
    rocket.attach(Compression::fairing())
}

#[cfg(not(feature = "compression"))]
fn setup_compression(rocket: Rocket<Build>) -> Rocket<Build> { rocket }

#[rocket::main]
async fn main() -> Result<(), rocket::Error> {
    let rocket = rocket::build()
        .mount("/", routes![sum])
        .mount("/", FileServer::from("../static"));

    // Workaround required due to missing support for attributes inside function blocks
    let rocket = setup_compression(rocket);

    let _ = rocket
        .launch()
        .await?;

    Ok(())
}