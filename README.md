# MirrorMind

MirrorMind is a Kivy-based application that provides a customizable dashboard with various widgets. It includes features such as face recognition to switch profiles and a grid overlay for widget placement.

## Features

- **Face Recognition**: Automatically switch profiles based on face recognition. (Comming Soon)
- **Customizable Widgets**: Add and resize widgets on the dashboard.
- **Grid Overlay**: Visual grid overlay to assist with widget placement.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/mirrormind.git
    cd mirrormind
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

Run the application:
```sh
python src/main.py
```
## Project Structure

- `main.py`: Main application entry point.
- `main.kv`: Kivy language file for UI layout.
- `widgets`: Directory containing widget implementations.
- `face_recognition.py`: Face recognition logic.
- `profile_manager.py`: Profile management logic.


## Contributing

1. Fork the repository.
2. Create a new branch (git checkout -b feature-branch).
3. Commit your changes (git commit -am 'Add new feature').
4. Push to the branch (git push origin feature-branch).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License.