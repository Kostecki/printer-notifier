#!/usr/bin/env zx

const rawConfig = await fs.readFile("./config.json");
const config = JSON.parse(rawConfig);

const Unifi = require("node-unifi");
const unifi = new Unifi.Controller({
  host: config.unifi_host,
  port: config.unifi_port,
  sslverify: false,
});

const tg_headerOptions = {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: {
    chat_id: config.tg_chatId,
    parse_mode: "HTML",
  },
};

const sendNotification = async (text) => {
  const body = JSON.stringify({ ...tg_headerOptions.body, text });

  return await fetch(
    `https://api.telegram.org/bot${config.tg_apikey}/sendMessage`,
    { ...tg_headerOptions, body }
  )
    .then((resp) => {
      if (!resp.ok) {
        throw resp;
      }
    })
    .catch((error) => {
      error.json().then(({ description }) => {
        console.error(description);
      });
    });
};

(async () => {
  try {
    await unifi.login(config.unifi_user, config.unifi_pass);

    const clientData = await unifi.getClientDevices();
    const client = clientData.find(
      (client) => client.mac === config.printer_mac
    );

    if (client && client.uptime > 3600) {
      const prettyDate = new Date(client.uptime * 1000)
        .toISOString()
        .substr(11, 8);

      sendNotification(
        `<b>Brother HL-2270W</b> \nThe printer has been on for ${prettyDate}`
      );
    }

    await unifi.logout();
  } catch (error) {
    console.error(error);
  }
})();
