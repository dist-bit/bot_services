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

## 🌟 Advanced Examples

Let's dive into some more complex examples to showcase the true power and flexibility of our Plug and Play Chat System:

### 1. AI-Powered Financial Advisor Bot

This bot combines natural language processing, real-time data fetching, and complex calculations to provide personalized financial advice.

```python
import yfinance as yf
from langchain.tools import tool
from implementations.abstract_functions_client import AbstractClientFunctions
import numpy as np

class FinancialAdvisorFunctions(AbstractClientFunctions):
    def __init__(self, db, session):
        self.db = db
        self.session = session

    @staticmethod
    @tool
    def analyze_stock(ticker: str) -> dict:
        """Analyze a stock and provide key metrics."""
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "name": info['longName'],
            "sector": info['sector'],
            "pe_ratio": info['trailingPE'],
            "dividend_yield": info['dividendYield'],
            "analyst_rating": info['recommendationKey']
        }

    @staticmethod
    @tool
    def calculate_portfolio_risk(tickers: list, weights: list) -> float:
        """Calculate the risk of a portfolio given stock tickers and weights."""
        data = yf.download(tickers, period="1y")['Adj Close']
        returns = data.pct_change()
        cov_matrix = returns.cov()
        portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
        return np.sqrt(portfolio_variance)

    @staticmethod
    @tool
    def recommend_portfolio(risk_tolerance: str, investment_amount: float) -> dict:
        """Recommend a portfolio based on risk tolerance and investment amount."""
        risk_profiles = {
            "low": [("GOVT", 0.4), ("VCSH", 0.3), ("VTI", 0.2), ("VXUS", 0.1)],
            "medium": [("VTI", 0.4), ("VXUS", 0.3), ("BND", 0.2), ("GLD", 0.1)],
            "high": [("QQQ", 0.4), ("ARKK", 0.3), ("MTUM", 0.2), ("BTCUSD=X", 0.1)]
        }
        profile = risk_profiles.get(risk_tolerance.lower(), risk_profiles["medium"])
        return {
            "portfolio": [{"ticker": ticker, "allocation": weight * investment_amount} 
                          for ticker, weight in profile],
            "total_investment": investment_amount
        }

    def get_openai_tools(self):
        return [
            FinancialAdvisorFunctions.analyze_stock,
            FinancialAdvisorFunctions.calculate_portfolio_risk,
            FinancialAdvisorFunctions.recommend_portfolio,
        ]
```

### 2. Multi-Language Travel Assistant with Image Recognition

This sophisticated bot can understand multiple languages, provide travel recommendations, and even analyze images of landmarks.

```python
from langchain.tools import tool
from implementations.abstract_functions_client import AbstractClientFunctions
from googletrans import Translator
from transformers import pipeline
import requests

class TravelAssistantFunctions(AbstractClientFunctions):
    def __init__(self, db, session):
        self.db = db
        self.session = session
        self.translator = Translator()
        self.image_classifier = pipeline("image-classification", model="microsoft/resnet-50")

    @staticmethod
    @tool
    def translate_text(text: str, target_language: str) -> str:
        """Translate given text to the target language."""
        translator = Translator()
        translation = translator.translate(text, dest=target_language)
        return translation.text

    @staticmethod
    @tool
    def get_flight_info(origin: str, destination: str, date: str) -> dict:
        """Get flight information for a given route and date."""
        # This would typically involve calling an external API
        # For demonstration, we'll return mock data
        return {
            "airline": "Sky Airlines",
            "flight_number": "SA123",
            "departure": "08:00 AM",
            "arrival": "11:30 AM",
            "price": "$299.99"
        }

    async def recognize_landmark(self, image_url: str) -> dict:
        """Recognize a landmark from an image URL."""
        response = self.session.get(image_url)
        image = response.content
        results = self.image_classifier(image)
        return {
            "landmark": results[0]['label'],
            "confidence": results[0]['score']
        }

    @staticmethod
    @tool
    def get_local_recommendations(location: str, preference: str) -> list:
        """Get local recommendations based on location and preference."""
        # This would typically involve calling an external API like Google Places
        # For demonstration, we'll return mock data
        recommendations = {
            "restaurant": ["La Bella Italia", "Sushi Heaven", "Burger Palace"],
            "museum": ["National History Museum", "Modern Art Gallery", "Science Center"],
            "park": ["Central Park", "Riverside Walk", "Botanical Gardens"]
        }
        return recommendations.get(preference, ["No recommendations found"])

    def get_media_tools(self):
        return {
            "recognize_landmark": self.recognize_landmark,
        }

    def get_openai_tools(self):
        return [
            TravelAssistantFunctions.translate_text,
            TravelAssistantFunctions.get_flight_info,
            TravelAssistantFunctions.get_local_recommendations,
        ]
```

### 3. Advanced Healthcare Assistant with Symptom Checking and Appointment Scheduling

This complex bot can perform initial symptom assessments, provide health information, and manage appointment scheduling.

```python
from langchain.tools import tool
from implementations.abstract_functions_client import AbstractClientFunctions
import datetime
import random

class HealthcareAssistantFunctions(AbstractClientFunctions):
    def __init__(self, db, session):
        self.db = db
        self.session = session

    @staticmethod
    @tool
    def check_symptoms(symptoms: list) -> dict:
        """Perform an initial assessment of symptoms."""
        # This would typically involve a more complex medical knowledge base
        # For demonstration, we'll use a simplified logic
        severity_score = len(symptoms) * random.randint(1, 3)
        if severity_score > 10:
            recommendation = "Please seek immediate medical attention."
        elif severity_score > 5:
            recommendation = "It's advisable to consult with a doctor soon."
        else:
            recommendation = "Monitor your symptoms. If they persist, consult a doctor."
        
        return {
            "severity": severity_score,
            "recommendation": recommendation
        }

    @staticmethod
    @tool
    def get_drug_info(drug_name: str) -> dict:
        """Retrieve information about a specific drug."""
        # This would typically involve querying a pharmaceutical database
        # For demonstration, we'll return mock data
        return {
            "name": drug_name,
            "uses": "Treatment of bacterial infections",
            "side_effects": ["Nausea", "Dizziness", "Headache"],
            "interactions": ["Alcohol", "Warfarin"],
            "precautions": "Do not use if allergic to penicillin"
        }

    @staticmethod
    @tool
    def schedule_appointment(department: str, preferred_date: str) -> dict:
        """Schedule a doctor's appointment."""
        # This would typically interface with a hospital's scheduling system
        # For demonstration, we'll simulate scheduling logic
        preferred_date = datetime.datetime.strptime(preferred_date, "%Y-%m-%d")
        scheduled_date = preferred_date + datetime.timedelta(days=random.randint(0, 5))
        return {
            "department": department,
            "doctor": f"Dr. {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}",
            "date": scheduled_date.strftime("%Y-%m-%d"),
            "time": f"{random.randint(9, 16):02d}:00"
        }

    async def analyze_medical_image(self, image_url: str) -> dict:
        """Analyze a medical image (X-ray, MRI, etc.)."""
        # This would typically involve complex image processing and ML models
        # For demonstration, we'll return a simulated analysis
        analysis_results = {
            "image_type": random.choice(["X-ray", "MRI", "CT Scan"]),
            "findings": random.choice(["No abnormalities detected", "Possible fracture detected", "Further examination required"]),
            "confidence": round(random.uniform(0.7, 0.99), 2)
        }
        return analysis_results

    def get_media_tools(self):
        return {
            "analyze_medical_image": self.analyze_medical_image,
        }

    def get_openai_tools(self):
        return [
            HealthcareAssistantFunctions.check_symptoms,
            HealthcareAssistantFunctions.get_drug_info,
            HealthcareAssistantFunctions.schedule_appointment,
        ]
```

These advanced examples demonstrate how our Plug and Play Chat System can be adapted to handle complex scenarios in finance, travel, and healthcare. By simply defining these function classes, you can create sophisticated chatbots capable of performing intricate tasks and providing valuable insights to users.

Remember, the true power of our system lies in its flexibility - you can easily combine functions from different domains or add new functions to create a uniquely tailored chatbot for your specific needs!


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