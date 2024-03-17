// use std::env;

// // define a function that returns a list of files in a directory
// fn list_files(dir: &str) -> std::io::Result<()> {
//     let paths = std::fs::read_dir(dir)?;

//     for path in paths {
//         println!("Name: {}", path.unwrap().path().display());
//     }

//     Ok(())
// }

// match env::home_dir() {
//     Some(path) => println!("{}", path.display()),
//     None => println!("Impossible to get your home dir!"),
// }

// // let paths = fs::read_dir("./").unwrap();
// let path_name = env
//     ::home_dir()
//     .unwrap()
//     .unwrap()
//     .join("Documents")
//     .join("video2motion-animplayer")
//     .join("public")
//     .join("anim-json");

// let paths = fs::read_dir(&path_name).unwrap();

// for path in paths {
//     println!("Name: {}", path.unwrap().path().display());
// }
