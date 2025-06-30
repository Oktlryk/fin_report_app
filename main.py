import sys
import os

# Add the farg directory to Python path if main.py is in the root
# This allows running 'python main.py' from the root directory
# Assumes 'farg' is a subdirectory in the same directory as main.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))


try:
    from farg.ui.app import demo # Assuming demo is globally defined in farg.ui.app
    if __name__ == '__main__':
        print("Starting FARG application from main.py...")
        print("Ensure you have all dependencies installed (e.g., from requirements.txt).")

        # The Gradio 'demo' object should be defined at the module level in farg.ui.app.py
        # The if __name__ == '__main__' block in farg.ui.app.py should be removed or
        # modified if main.py is the sole entry point.

        if demo:
            print(f"Found Gradio demo object: {type(demo)}")
            # Set server_name and server_port for consistency if needed, or let Gradio choose.
            # demo.launch(server_name="0.0.0.0", server_port=7860) # Example with specific host/port
            demo.launch() # Uses default localhost and port (usually 7860)
        else:
            print("Error: Gradio 'demo' object not found or not imported correctly from farg.ui.app.")

except ModuleNotFoundError as e:
    print(f"Error: Could not import FARG UI. ModuleNotFoundError: {e}")
    print("Details:")
    print(f"  sys.path used for import attempt: {sys.path}")
    print(f"  Current working directory: {os.getcwd()}")
    print("\nPlease ensure that:")
    print("  1. You are running `python main.py` from the project root directory (the one containing `main.py` and the `farg` folder).")
    print("  2. The 'farg' directory exists at the same level as `main.py`.")
    print("  3. All dependencies, especially `gradio`, are installed.")
    print("  4. There are no circular import issues within the `farg` package.")
except ImportError as e:
    print(f"Import error: {e}")
    print("This might be due to missing dependencies or issues with relative/absolute imports within the farg package.")
    print("Please check that all required libraries (gradio, langchain-core, etc.) are installed.")
except AttributeError as e:
    print(f"AttributeError: {e}.")
    print("This might mean the 'demo' object is not directly accessible or is named differently in farg.ui.app.")
    print("Ensure 'demo = gr.Interface(...)' is at the global scope in farg.ui.app.py.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    print("Please check the traceback for more details.")
