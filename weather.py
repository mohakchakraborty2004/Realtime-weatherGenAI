import google.generativeai as genai
import json
import requests

# Configure the API key
genai.configure(api_key="")

# Define tools/functions
def get_weather(city):
      # Implement your weather function
      print("🔨 Tool Called: get_weather", city)
      
      url = f"https://wttr.in/{city}?format=%C+%t"
      result = requests.get(url)

      if result.status_code == 200:
          return f"The weather in {city} is {result.text}."
      return "Something went wrong"

def run_command(command):
    
    return f"Mock command output for '{command}'"

available_tools = {
    "get_weather": {
        "fn": get_weather,
        "description": "Takes a city name as an input and returns the current weather for the city"
    },
    "run_command": {
        "fn": run_command,
        "description": "Takes a command as input to execute on system and returns output"
    }
}

# system prompt
system_prompt = f"""
    You are a helpful AI Assistant who is specialized in resolving user queries.
    You work on start, plan, action, observe mode.
    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
    Wait for the observation and based on the observation from the tool call resolve the user query.
    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query
    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}
    Available Tools:
    - get_weather: Takes a city name as an input and returns the current weather for the city
    - run_command: Takes a command as input to execute on system and returns output
    
    Example:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}
"""

# Initialize the model and create a chat session
model = genai.GenerativeModel('gemini-2.0-flash', 
 generation_config={"response_mime_type": "application/json"})
chat = model.start_chat(history=[])

# Send the system prompt first
chat.send_message(system_prompt)

while True:
    user_query = input('> ')
    
    # Process user query in a loop to handle the step-by-step process
    response = chat.send_message(user_query)
    
    while True:
        
        try:
            # Parse the JSON response
            parsed_output = json.loads(response.text)
            
            
            if parsed_output.get("step") == "plan":
                print(f"🧠: {parsed_output.get('content')}")
                response = chat.send_message("Continue to the action step based on this plan.")
                continue
            
            elif parsed_output.get("step") == "action":
                print(f"🧠: let's look for the weather{parsed_output.get('content')}")
                tool_name = parsed_output.get("function")
                tool_input = parsed_output.get("input")
                if available_tools.get(tool_name, False) != False:
                    # print("hellooooooooooooo")
                    output = available_tools[tool_name].get("fn")(tool_input)
                    response = chat.send_message(json.dumps({"step": "observe", "output": output}))
                    continue

            elif parsed_output.get("step") == "output":
                print(f"🤖: {parsed_output.get('content')}")
                break
            
            else : 
               response = chat.send_message("Please proceed to the next step in the sequence.")
                
        except json.JSONDecodeError:
            print("Error parsing JSON response. Retrying...")
            chat.send_message("Remember to respond with valid JSON following the specified format.")