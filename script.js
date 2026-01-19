require("dotenv").config();
const tmi = require("tmi.js");
const fs = require("fs");
const axios = require("axios");

// Configuration de la connexion
const opts = {
  identity: {
    username: process.env.TWITCH_USERNAME,
    password: process.env.TWITCH_OAUTH_TOKEN,
  },
  channels: [],
};

// Créer un client
const client = new tmi.client(opts);

// Dictionnaire pour stocker les couleurs et leurs occurrences par streamer
const colorOccurrencesByStreamer = {};

// Fonction pour obtenir un nouveau token d'accès
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
    console.log("Nouveau token d'accès généré avec succès.");
    return newAccessToken;
  } catch (error) {
    console.error(
      "Erreur lors de la génération du nouveau token d'accès :",
      error,
    );
    throw error;
  }
}

// Fonction pour récupérer les 100 meilleurs streamers Twitch
async function getTopStreamers() {
  try {
    const response = await axios.get("https://api.twitch.tv/helix/streams", {
      headers: {
        "Client-ID": process.env.TWITCH_CLIENT_ID,
        Authorization: `Bearer ${process.env.TWITCH_OAUTH_TOKEN}`,
      },
      params: {
        first: 100,
      },
    });

    //const topStreamers = response.data.data.map((stream) => stream.user_name);
    //console.log("Top Streamers: %o", topStreamers);
    //opts.channels = topStreamers;
    opts.channels = ["Chloe__IRL"];
    topStreamers = opts.channels;
    console.log("Channels to join: %o", opts.channels);

    // Initialiser les dictionnaires pour chaque streamer
    topStreamers.forEach((streamer) => {
      colorOccurrencesByStreamer[streamer] = {};
    });

    client.connect();
  } catch (error) {
    if (error.response && error.response.status === 401) {
      // Si le token est invalide, générer un nouveau token
      try {
        const newToken = await generateNewOAuthToken();
        process.env.TWITCH_OAUTH_TOKEN = newToken;
        opts.identity.password = newToken;
        // Réessayer de récupérer les meilleurs streamers
        await getTopStreamers();
      } catch (tokenError) {
        console.error("Échec de la génération du nouveau token :", tokenError);
        process.exit(1); // Arrêter le script en cas d'échec
      }
    } else {
      console.error(
        "Erreur lors de la récupération des meilleurs streamers :",
        error,
      );
    }
  }
}

// Écouter les messages de chat
client.on("message", (channel, tags, message, self) => {
  const content = message.toLowerCase();
  const numberSpaces = (content.match(/\s+/g) || []).length;
  if (content.includes("?") && numberSpaces > 2) {
    console.log("QUESTION DETECTED, querying RAG...");
    axios
      .post("http://localhost:5000/query", {
        question: message,
      })
      .then((response) => {
        const answer = response.data.answer;
        console.log(`RAG Answer: ${answer}`);
        client.say(channel, answer).catch((err) => {
          console.error("Error sending message to chat:", err.message);
        });
      })
      .catch((error) => {
        console.error("Error querying RAG:", error);
      });
  }

  if (self) return;

  const userColor = tags.color;
  const streamer = channel.slice(1); // Retirer le '#' du nom du canal

  // Mettre à jour le dictionnaire des occurrences de couleurs pour le streamer
  if (userColor && colorOccurrencesByStreamer[streamer]) {
    if (colorOccurrencesByStreamer[streamer][userColor]) {
      colorOccurrencesByStreamer[streamer][userColor]++;
      console.log(
        `🟢 ${tags["display-name"]} (couleur: ${userColor}) sur le stream de ${streamer}: ${message}`,
      );
    } else {
      colorOccurrencesByStreamer[streamer][userColor] = 1;
      console.log(
        `🟢 ${tags["display-name"]} (couleur: ${userColor}) sur le stream de ${streamer}: ${message}`,
      );
    }
  } else {
    if (userColor != null) {
      colorOccurrencesByStreamer[streamer] = {};
      colorOccurrencesByStreamer[streamer][userColor] = 1;
      console.log(
        `🟡 ${tags["display-name"]} (couleur: ${userColor}) sur le stream de ${streamer}: ${message}`,
      );
    } else {
      console.log("🔴 No color for this user ");
    }
  }
});

// Gestionnaire pour exporter les dictionnaires dans un CSV lors de l'arrêt du script
process.on("SIGINT", () => {
  // Exporter les occurrences des couleurs par streamer
  let csvDataColors = "Streamer,Color,Count\n";
  for (const [streamer, colors] of Object.entries(colorOccurrencesByStreamer)) {
    for (const [color, count] of Object.entries(colors)) {
      csvDataColors += `${streamer},${color},${count}\n`;
    }
  }
  fs.writeFileSync("color_occurrences_by_streamer4.csv", csvDataColors);
  console.log(
    "\nOccurrences des couleurs par streamer exportées dans color_occurrences_by_streamer4.csv",
  );

  // Exporter la liste des streamers
  const streamerNames = Object.keys(colorOccurrencesByStreamer);
  const csvDataStreamers = "Streamer\n" + streamerNames.join("\n");
  fs.writeFileSync("streamers_lis4t.csv", csvDataStreamers);
  console.log("Liste des streamers exportée dans streamers_list4.csv");

  process.exit();
});

// Écouter les utilisateurs qui rejoignent le chat
client.on("join", (channel, username, self) => {
  if (self) return;

  console.log(`${username} a rejoint le chat`);
});

// Écouter les utilisateurs qui quittent le chat
client.on("part", (channel, username, self) => {
  if (self) return;

  console.log(`${username} a quitté le chat`);
});

// Récupérer les meilleurs streamers et démarrer le client
getTopStreamers();
