use std::fs;
use std::fs::File;
use std::io::{ BufReader, Cursor };
use std::path::Path;
use std::env;

use anyhow::Result;
use headless_chrome::{ protocol::cdp::Page::CaptureScreenshotFormatOption, Browser, LaunchOptions };

mod utils;

fn take_screenshot() -> Result<()> {
    // Create a headless browser, navigate to wikipedia.org, wait for the page
    // to render completely, take a screenshot of the entire page
    // in JPEG-format using 75% quality.
    let options = LaunchOptions::default_builder()
        .build()
        .expect("Couldn't find appropriate Chrome binary.");
    let browser = Browser::new(options)?;
    let tab = browser.new_tab()?;
    let jpeg_data = tab
        .navigate_to("http://localhost:5173/glb")?
        .wait_until_navigated()?
        .capture_screenshot(CaptureScreenshotFormatOption::Jpeg, Some(75), None, true)?;

    let path = Path::new(".");

    fs::write(path.join("frames").join("screenshot.jpg"), jpeg_data)?;

    // // Browse to the WebKit-Page and take a screenshot of the infobox.
    // let png_data = tab
    //     .navigate_to("http://localhost:5173/glb")?
    //     .wait_for_element("#done")?
    //     .capture_screenshot(CaptureScreenshotFormatOption::Png)?;

    // fs::write(path.join("frames").join("screenshot.png"), png_data)?;

    println!("Screenshots successfully created.");
    Ok(())
}

fn main() -> Result<()> {
    let path = Ok(match env::home_dir() {
        Some(path) => println!("{}", path.display()),
        None => println!("Impossible to get your home dir!"),
    });

    // get home_dir as a PathBuf

    let path_name = path
        .unwrap()
        .unwrap()
        .join("Documents")
        .join("video2motion-animplayer")
        .join("public")
        .join("anim-json");

    // let paths = fs::read_dir(&path_name).unwrap();

    // for path in paths {
    //     println!("Name: {}", path.unwrap().path().display());
    // }

    Ok(())

    // take_screenshot()
}
