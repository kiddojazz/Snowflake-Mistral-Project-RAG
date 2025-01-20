from enum import Enum



class PagesMarkdowns(Enum):
    CHAT_MARKDOWN_HEADER = """# Database Query and Interactive AI Chat

Welcome to the **Database Query and Interactive AI Chat** page! Follow the steps below to query the database and interact with AI for further insights.

---
"""
    CHAT_MARKDOWN = """

### **How to Use This Page**

1. **Send a Prompt**:
   - Use the **chat input box** at the bottom of the page to send your query.
   - If your query is related to the database table, a **dataframe** will be generated based on the backend database.

2. **Handle Non-Table Responses**:
   - If your query is **not related** to the database table, the response will be plain text.
   - Kindly focus on **database-related queries** to generate a dataframe.

3. **Activate AI Chat in Sidebar**:
   - Once a dataframe has been generated, you can enable the **AI Chat** for further analysis or discussions.
   - Toggle the **"Activate Sidebar"** option in the sidebar to chat with the AI, which uses the dataframe as context.

4. **Explore More**:
   - After you're done, you can return to the chat input and send a new prompt to explore additional information from the table.

---

### **Notes**
- Ensure your queries are **database-focused** for accurate dataframe generation.
- Use the **AI Chat** to gain deeper insights based on the generated dataframe.
- Repeat the process to explore different aspects of the database.

Enjoy your interactive data exploration experience!
"""

    DASHBOARD_MARKDOWN_HEADER = """# Interactive Dashboard Generator

Welcome to the **Interactive Dashboard Generator**! 🎉

This tool allows you to **generate dynamic dashboards** based on your specific data queries. Simply enter your query below, and the system will process your request to build the desired dashboard in real-time.
"""

    DASHBOARD_MARKDOWN = """## How it Works:
1. **Enter Your Query**: Provide the type of visualization or data analysis you would like to see.
2. **Generate Dashboard**: Once the query is submitted, the system will automatically generate a corresponding dashboard with the appropriate charts and widgets.
3. **Interactive Exploration**: Use the interactive controls (like sliders, dropdowns, and buttons) to explore and adjust the dashboard to your preferences. (*Feature Coming Soon*)


### Example Queries:
- "Generate a line chart showing sales over time."
- "Create a bar chart comparing revenue across different regions."
- "Show a pie chart of customer segmentation by age group."

💡 **Tip**: Be as specific as possible with your query to get the most accurate dashboard.

---


### Enter Your Query:
Below is a field where you can type your query. Once entered, hit the button to generate your dashboard!
"""
    SPEECH_TO_SPEECH_MARKDOWN = """"""

    SPEECH_TO_TEXT_MARKDOWN = """"""

    TEXT_TO_SPEECH_MARKDOWN = """"""
