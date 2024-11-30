
use tokio::io::{self,AsyncReadExt, AsyncWriteExt};
use tokio_native_tls::TlsConnector;
use tokio::net::TcpStream;


async fn establish_connection(host: &str, port: &str) -> io::Result<tokio_native_tls::TlsStream<TcpStream>> {
    // Connect to the server
    let stream = TcpStream::connect(format!("{}:{}", host, port)).await?;

    // Upgrade the control connection to TLS
    let tls_connector = TlsConnector::from(
        match native_tls::TlsConnector::builder().use_sni(true).build() {
            Ok(connector) => {
                println!("Upgraded to TLS");
                connector
            },
            Err(e) => {
                eprintln!("Failed to build TlsConnector: {}", e);
                return Err(std::io::Error::new(std::io::ErrorKind::Other, e));
            }
        }
    );

    // Attempt to connect
    match tls_connector.connect(host, stream).await {
        Ok(stream) => {
            println!("Connected to {}", host);
            Ok(stream)
        },
        Err(e) => {
            eprintln!("Failed to connect using TlsConnector: {}", e);
            Err(std::io::Error::new(std::io::ErrorKind::Other, e))
        }
    }
}

#[tokio::main]
async fn main() -> io::Result<()> {
    let host = "gra1.logs.ovh.com";
    let port = "12202";

    let mut tls_stream = establish_connection(host, port).await?;

    let mut accumulated_lines = String::new();
    let mut stdin = tokio::io::BufReader::new(tokio::io::stdin());
    let mut buf = [0u8; 1];

    while let Ok(size) = stdin.read_exact(&mut buf).await {
        if size == 0 {
            break; // EOF or stream closed
        }

        match buf[0] {
            b'\0' => {
                accumulated_lines.push('\0');
                
                // Send the message over the TLS stream
                let _ = match tls_stream.write_all(accumulated_lines.as_bytes()).await {
                    Ok(_) => {
                        let _ = match tls_stream.flush().await {
                            Ok(_) => {
                                println!("SENT and FLUSHED '{}'", accumulated_lines);
                            },
                            Err(flush_err) => {
                                eprintln!("Error flushing data: {}", flush_err);
                            }
                        };

                        tls_stream.shutdown().await?;
                        tls_stream = establish_connection(host, port).await?;
                    },
                    Err(e) => {
                        eprintln!("An error occurred: {}", e);
                    }
                };

                // Clear the accumulated lines
                accumulated_lines.clear();
            },
            b => accumulated_lines.push(b as char),
        }
    }

    Ok(())
}




