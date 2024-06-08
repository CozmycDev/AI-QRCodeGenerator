# QR Code Generator

This Python script generates a QR code using the AIHorde API. It allows you to input a URL and a prompt for generating a scannable QR code image.

![QR Image](/example-2.webp?raw=true "https://discord.dreamdiffusion.net/")
`Prompt:` *stars, nebula, space, high quality, detailed*\
(https://discord.dreamdiffusion.net/)

## Prerequisites

Before running the script, ensure you have the following installed:
- [Python 3.x](https://www.python.org/downloads/)
- The necessary Python packages listed in `requirements.txt`

Alternatively, you can use the provided Windows binary packaged with PyInstaller in the [releases](https://github.com/CozmycDev/AI-QRCodeGenerator/releases) section. This binary eliminates the need to install Python and allows for faster generations with the AIHorde using a shared key instead of using the slower anonymous key found in-source: `0000000000`

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/CozmycDev/AI-QRCodeGenerator.git
   ```

2. Navigate to the project directory:
   ```
   cd AI-QRCodeGenerator
   ```

3. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the script `main.py`:
   ```
   python main.py
   ```

The script will prompt you to enter a URL and an image prompt. After generating the QR code, it will display the URL to the generated image.

## Image Generation

The image generation is provided by crowdsourced compute a la [AIHorde](https://aihorde.net/).

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvement, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).