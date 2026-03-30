require("dotenv").config();
const tmi = require("tmi.js");
const fs = require("fs");
const axios = require("axios");

const opts = {
  identity: {
    username: process.env.TWITCH_USERNAME,
    // Chat OAuth token must be a user token with "oauth:" prefix
    password: process.env.TWITCH_CHAT_OAUTH_TOKEN,
  },
  channels: [],
};

// Create a client
const client = new tmi.client(opts);

// Function to get a new access token
async function generateNewOAuthToken() {
  const clientId = process.env.TWITCH_CLIENT_ID;
  const clientSecret = process.env.TWITCH_CLIENT_SECRET;
  const tokenUrl = "https://id.twitch.tv/oauth2/token";

  try {
    const response = await axios.post(tokenUrl, null, {
      params: {
        client_id: clientId,
        client_secret: clientSecret,
        grant_type: "client_credentials",
      },
    });

    const newAccessToken = response.data.access_token;
    console.log("Successfully generated new access token.");
    return newAccessToken;
  } catch (error) {
    console.error("Error generating new access token:", error);
    throw error;
  }
}

// Function to get the top 100 Twitch streamers
async function getTopStreamers() {
  try {
    const response = await axios.get("https://api.twitch.tv/helix/streams", {
      headers: {
        "Client-ID": process.env.TWITCH_CLIENT_ID,
        Authorization: `Bearer ${process.env.TWITCH_APP_ACCESS_TOKEN}`,
      },
      params: {
        first: 100,
      },
    });

    //const topStreamers = response.data.data.map((stream) => stream.user_name);
    //console.log("Top Streamers: %o", topStreamers);
    //opts.channels = topStreamers;
    opts.channels = ["Light_srh"];
    topStreamers = opts.channels;
    console.log("Channels to join: %o", opts.channels);

    client.connect().catch((error) => {
      console.error("Error connecting to Twitch chat:", error);
    });
    console.log("Connected to Twitch chat, listening for messages...");
  } catch (error) {
    if (error.response && error.response.status === 401) {
      try {
        const newToken = await generateNewOAuthToken();
        process.env.TWITCH_APP_ACCESS_TOKEN = newToken;
        // Retry fetching the top streamers
        await getTopStreamers();
      } catch (tokenError) {
        console.error("Failed to generate new token:", tokenError);
        process.exit(1); // Stop the script on failure
      }
    } else {
      console.error("Error fetching top streamers:", error);
    }
  }
}

// Listen to chat messages
client.on("message", (channel, tags, message, self) => {
  if (self) return;

  const username = tags["display-name"];
  const streamer = channel.slice(1);

  console.log(`[${streamer}] ${username}: ${message}`);

  // DDetect questions and query the RAG
  const content = message.toLowerCase();
  const numberSpaces = (content.match(/\s+/g) || []).length;

  if (content.includes("?") && numberSpaces > 2 && content.length < 50) {
    console.log("QUESTION DETECTED, querying RAG...");
    axios
      .post("http://localhost:5000/query", {
        question: message,
      })
      .then((response) => {
        const answer = response.data.answer;
        console.log(`RAG Answer: ${answer}`);
        client.say(channel, answer).catch((err) => {
          console.error("Error sending message to chat:", err);
        });
      })
      .catch((error) => {
        console.error("Error querying RAG:", error);
      });
  }
});

// Démarrer le processus
getTopStreamers();
