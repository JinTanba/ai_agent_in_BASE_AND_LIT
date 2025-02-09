//@ts-nocheck
import { Midjourney } from "midjourney";

const SERVER_ID = process.env.SERVER_ID;
const CHANNEL_ID = process.env.CHANNEL_ID;
const SALAI_TOKEN = process.env.SALAI_TOKEN;

if (!SERVER_ID || !CHANNEL_ID || !SALAI_TOKEN) {
  throw new Error("Required environment variables are not set. Please check .env file.");
}

const client = new Midjourney({
  ServerId: SERVER_ID,
  ChannelId: CHANNEL_ID,
  SalaiToken: SALAI_TOKEN,
  Debug: true,
  Ws: true,
});

export async function generateImg(prompt: string): Promise<string> {
    await client.init();
    
    const Imagine = await client.Imagine(
      prompt,
      (uri: string, progress: string) => {
        console.log('---------------------------------')
        console.log("loading", uri, "progress", progress);
      }
    );

    if(Imagine === null) {
      throw new Error("Failed to generate initial image");
    }

    const V1CustomID = Imagine.options?.find((o) => o.label === "V1")?.custom;
    if (!V1CustomID) {
      console.log("no V1");
      return Imagine.uri;
    }

    // Varition V1
    const Varition = await client.Custom({
      msgId: Imagine.id,
      flags: Imagine.flags,
      customId: V1CustomID,
      content: prompt, //remix mode require content
      loading: (uri: string, progress: string) => {
        console.log("loading", uri, "progress", progress);
        console.log('🔥🔥🔥🔥', uri)
      },
    });

    const hash = Varition?.hash;
    if (!hash) {
      // バリエーションの生成に失敗した場合は元の画像のURLを返す
      return Imagine.uri;
    }

    // CDN URLの生成
    const imageUrl = `https://cdn.midjourney.com/${hash}/0_0.png`;
    console.log(imageUrl)
    client.Close();
    return imageUrl;
}

// ファイルが直接実行された場合のサンプル実行
if (process.argv[1].endsWith('generateImg.ts')) {
    const theme = "Playful Pet";
    const style = "digital art style";
    const subject = "kitten";
    const background = "cozy living room with soft lighting";
    const main_color = "warm orange and red tones";
    const detailed_description = "A small kitten enthusiastically playing with a red ball of yarn, creating a heartwarming and dynamic scene";

    const samplePrompt = `${theme} ${style} ${subject} ${background} ${main_color} ${detailed_description}`;
    console.log("Generating image with sample prompt:", samplePrompt);
    
    generateImg(samplePrompt)
        .then(url => {
            console.log("Generated image URL:", url);
        })
        .catch(error => {
            console.error("Error generating image:", error);
        });
}
