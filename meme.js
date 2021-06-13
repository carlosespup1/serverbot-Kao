require("dotenv").config();
const Discord = require("discord.js");
const axios = require("axios");
const cheerio = require("cheerio");


const linkMemes = [ // the links where is going to scrap
  "https://www.reddit.com/r/MAAU/top/",
  "https://www.reddit.com/r/DylanteroYT/hot/",
  "https://www.reddit.com/r/linuxmemes/hot",
  "https://www.reddit.com/r/linuxmemes/new/",
  "https://www.reddit.com/r/linuxmemes/top/",
  "https://www.reddit.com/r/ProgrammerHumor/hot/",
  "https://www.reddit.com/r/ProgrammerHumor/new/",
  "https://www.reddit.com/r/ProgrammerHumor/top/",
  "https://www.reddit.com/r/MAAU/hot/",
  "https://www.reddit.com/r/MAAU/new/",
];

var img = [];

const client = new Discord.Client(),
  commands = {
    "*meme": async function (msg) {
      let embed = new Discord.MessageEmbed()
        .setTitle("meme")
        .setImage(img[Math.floor(Math.random() * img.length)]);
      msg.channel.send(embed); // send the embed with the image
      linkMemes.map((i) => {
        axios.get(i).then((r) => { // here is making the request
          let $ = cheerio.load(r.data);
          $("._2_tDEnGMLxpM6uOa2kaDB3").each((i, e) => { // the html property of the reddit page
            img.push($(e).attr("src"));
          });
        });
      });
    },
  };

client.on("ready", () => {
  console.log(`bot ready! ${client.user.tag}!`);
});
client.on("message", (msg) => {
  if (commands.hasOwnProperty(msg.content)) {
    commands[msg.content](msg);
  }
});
client.login(process.env.TOKEN); // login with the env
