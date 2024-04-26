use std::fs;
use std::path::Path;
use std::env;

use anyhow::Result;
use headless_chrome::{ protocol::cdp::Page::CaptureScreenshotFormatOption, Browser, LaunchOptions };

fn take_screenshot(url: &str) -> Result<()> {
    // Create a headless browser, navigate to wikipedia.org, wait for the page
    // to render completely, take a screenshot of the entire page
    // in JPEG-format using 75% quality.
    let options = LaunchOptions::default_builder()
        .build()
        .expect("Couldn't find appropriate Chrome binary.");
    let browser = Browser::new(options)?;
    let tab = browser.new_tab()?;

    tab.navigate_to(url)?;

    tab.wait_for_element("#done")?;

    let jpeg_data = tab.capture_screenshot(
        CaptureScreenshotFormatOption::Jpeg,
        Some(75),
        None,
        true
    )?;

    let path = Path::new(".");

    fs::write(path.join("screenshot.jpg"), jpeg_data)?;

    println!("Screenshots successfully created.");
    Ok(())
}

fn main() -> Result<()> {
    let mut url: String = "http://localhost:5173".to_string();

    let mut args = env::args().skip(1);
    while let Some(arg) = args.next() {
        match &arg[..] {
            "-q" | "--quiet" => {
                println!("Quiet mode is not supported yet.");
            }
            "-v" | "--verbose" => {
                println!("Verbose mode is not supported yet.");
            }
            "-u" | "--url" => {
                if let Some(arg_url) = args.next() {
                    url = arg_url;
                } else {
                    panic!("No value specified for parameter --config.");
                }
            }
            _ => {
                if arg.starts_with('-') {
                    println!("Unkown argument {}", arg);
                } else {
                    println!("Unkown positional argument {}", arg);
                }
            }
        }
    }

    // print config
    println!("taking screenshot from: {}", url);

    take_screenshot(url.as_str())
}
