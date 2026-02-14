import { GoogleGenAI, Type, Schema } from "@google/genai";
import { Message, AIResponse } from "../types";

// Ensure API Key exists
const API_KEY = process.env.API_KEY;
if (!API_KEY) {
  console.error("API_KEY is missing from environment variables.");
}

const ai = new GoogleGenAI({ apiKey: API_KEY });

const responseSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    text: {
      type: Type.STRING,
      description: "The conversational response to the user. Always include a brief summary or insight about the data if a chart is generated.",
    },
    chart: {
      type: Type.OBJECT,
      nullable: true,
      description: "Optional chart configuration if the user requested visualization or provided data suitable for a chart.",
      properties: {
        type: {
          type: Type.STRING,
          enum: ["bar", "line", "area", "pie", "scatter"],
          description: "The type of chart to render.",
        },
        title: {
          type: Type.STRING,
          description: "A descriptive title for the chart.",
        },
        description: {
          type: Type.STRING,
          description: "A short description of what the chart shows.",
        },
        xAxisLabel: {
          type: Type.STRING,
          description: "Label for the X-axis (e.g., 'Month', 'Year', 'Category').",
        },
        yAxisLabel: {
          type: Type.STRING,
          description: "Label for the Y-axis (e.g., 'Sales ($)', 'Count').",
        },
        data: {
          type: Type.ARRAY,
          description: "The data points for the chart.",
          items: {
            type: Type.OBJECT,
            properties: {
              name: {
                type: Type.STRING,
                description: "The category or X-axis label for this data point (e.g., 'Jan', 'Product A').",
              },
              series: {
                type: Type.ARRAY,
                description: "List of values for this category (supports multi-series).",
                items: {
                  type: Type.OBJECT,
                  properties: {
                    name: {
                      type: Type.STRING,
                      description: "The name of the series (e.g., 'Revenue', 'Cost').",
                    },
                    value: {
                      type: Type.NUMBER,
                      description: "The numeric value.",
                    },
                  },
                  required: ["name", "value"],
                },
              },
            },
            required: ["name", "series"],
          },
        },
      },
      required: ["type", "title", "data"],
    },
  },
  required: ["text"],
};

const SYSTEM_INSTRUCTION = `
You are ChartBot, an expert data visualization assistant.
Your goal is to help users visualize data through interactive charts.

Rules:
1. If the user provides data or asks for a visualization, ALWAYS generate a 'chart' object in the JSON response.
2. If the user's request is ambiguous, ask for clarification in the 'text' field.
3. For the 'chart' data, ensure it is realistic and helpful if the user asks for a generic example (e.g., "Show me a growth curve").
4. Keep the 'text' response concise but friendly. Explain the chart briefly if one is generated.
5. Supported chart types: bar, line, area, pie, scatter. Choose the best one for the data.
6. Return purely JSON adhering to the specified schema.
`;

export const sendMessageToGemini = async (
  history: Message[],
  newMessage: string
): Promise<AIResponse> => {
  try {
    const model = "gemini-3-flash-preview";

    // Convert history to API format
    // We only send the last few messages to keep context but save tokens, 
    // and we simplify the content to just text for the context 
    // (the model doesn't need to see its own raw JSON output from previous turns, just the logical conversation).
    const chatHistory = history.map((msg) => ({
      role: msg.role,
      parts: [{ text: msg.content }],
    }));

    const chat = ai.chats.create({
      model: model,
      history: chatHistory,
      config: {
        systemInstruction: SYSTEM_INSTRUCTION,
        responseMimeType: "application/json",
        responseSchema: responseSchema,
      },
    });

    const result = await chat.sendMessage({ message: newMessage });
    const responseText = result.text;

    if (!responseText) {
      throw new Error("Empty response from Gemini");
    }

    try {
      const parsedResponse = JSON.parse(responseText) as AIResponse;
      return parsedResponse;
    } catch (parseError) {
      console.error("JSON Parse Error:", parseError, responseText);
      return {
        text: "I generated a response, but it wasn't valid JSON. Here is the raw text: " + responseText,
      };
    }

  } catch (error) {
    console.error("Gemini API Error:", error);
    throw error;
  }
};
