# 🔌 Plug and Play Chat System

Welcome to the ultimate Plug and Play Chat System! This innovative framework allows you to create powerful, customized chatbots with minimal effort. Just plug in your functions, and you're ready to play!

## 🚀 Key Features

- **Truly Plug and Play**: Add your custom functions and watch your chatbot come to life!
- **Flexible Architecture**: Easily adapt the system to various use cases and industries.
- **Multi-Platform Support**: Works seamlessly with WhatsApp, Telegram, and more.
- **Dynamic Function Execution**: Intelligent routing of user inputs to appropriate functions.
- **Easy Configuration**: Simple setup process with environment variables and config files.

## 🏗️ System Architecture

Our Plug and Play Chat System is designed with modularity in mind:

1. **Main Application** (`main.py`): The entry point of your chatbot.
2. **WhatsApp Bot** (`whatsapp_bot.py`): Handles messaging platform specifics.
3. **Config** (`config.py`): Manages your chatbot's configuration.
4. **Custom Functions** (`my_custom_functions.py`): Where your magic happens!
5. **Controller** (`controller.py`): Orchestrates the conversation flow.
6. **ToolCaller** (`tool_caller.py`): Executes your custom functions dynamically.

## 🔧 Getting Started

1. Clone this repository:
   ```
   git clone https://github.com/your-repo/plug-and-play-chat-system.git
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables in a `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   ```

4. Create your custom functions (see next section).

5. Run your chatbot:
   ```
   python main.py
   ```

## 🧩 Creating Custom Functions

This is where the "Plug and Play" magic happens! Simply create a new Python file (e.g., `my_custom_functions.py`) and define your functions. Here's an example:

```python
from langchain.tools import tool
from implementations.abstract_functions_client import AbstractClientFunctions

class MyAwesomeFunctions(AbstractClientFunctions):
    def __init__(self, db, session):
        self.db = db
        self.session = session

    @staticmethod
    @tool
    def check_weather(location: str) -> str:
        """Check the weather for a given location."""
        # Your weather checking logic here
        return f"The weather in {location} is sunny!"

    @staticmethod
    @tool
    def book_appointment(date: str, time: str) -> bool:
        """Book an appointment for a given date and time."""
        # Your appointment booking logic here
        return True

    def get_media_tools(self):
        return {}  # Add any media processing functions here

    def get_openai_tools(self):
        return [
            MyAwesomeFunctions.check_weather,
            MyAwesomeFunctions.book_appointment,
        ]
```

That's it! Your custom functions are now ready to be used by the chatbot.

## ⚙️ Configuration

Update your `config.py` to include your new functions:

```python
class Config:
    def __init__(self):
        self.CLIENT_CONFIGURATIONS = {
            "default": {
                "media_functions": "my_awesome_functions",
                "functions_to_apply": [
                    "check_weather",
                    "book_appointment",
                ]
            }
        }
    
    # ... rest of the config class
```

## 🎭 Core Components

### ToolCaller

The `ToolCaller` is the brain of our Plug and Play system. It dynamically executes your custom functions based on user input.

```python
class ToolCaller:
    def __init__(self, client_functions: AbstractClientFunctions, functions_to_apply: List[Dict[str, Any]]):
        self.client_functions = client_functions
        self.tools = client_functions.get_openai_tools()
        self.functions_to_apply = functions_to_apply

    def process_input_tool(self, msg: str, function: str, report: str):
        # Magic happens here!
        # This method intelligently routes user input to your custom functions
```

### Controller

The `Controller` manages the conversation flow and uses the `ToolCaller` to process user inputs:

```python
class Controller:
    def __init__(self, client, db, promoter_robot, media_functions, tool_caller):
        self.tool_caller = tool_caller
        # ... other initializations

    async def handle_text_input(self, user_response: str, step_details: dict, client_id: str):
        tool_response = self.tool_caller.process_input_tool(
            user_response, step_details["function"], report_id)
        # Process the response and manage conversation flow
```

## 🌟 Examples

1. **Restaurant Booking Bot**:
   ```python
   @tool
   def check_table_availability(date: str, party_size: int) -> bool:
       # Your availability checking logic here
   
   @tool
   def make_reservation(date: str, party_size: int, name: str) -> dict:
       # Your reservation making logic here
   ```

2. **Weather Bot**:
   ```python
   @tool
   def get_weather_forecast(location: str, days: int) -> str:
       # Your weather forecasting logic here
   
   @tool
   def set_weather_alert(location: str, condition: str) -> bool:
       # Your weather alert setting logic here
   ```

## 🧪 Testing

Run tests to ensure your Plug and Play system is working correctly:

```
pytest tests/
```

## 🚀 Deployment

Deploy your Plug and Play Chat System on any Python-supporting platform:

1. **Heroku**: Use the provided Procfile.
2. **AWS Lambda**: Package your app and deploy as a Lambda function.
3. **Docker**: Use the Dockerfile to containerize your chatbot.

## 🤝 Contributing

We love contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get involved.

## 📄 License

This Plug and Play Chat System is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for more details.

---

Remember, with our Plug and Play Chat System, you're just a few functions away from your perfect chatbot. Happy coding! 🎉