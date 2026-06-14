import { Utility } from '../../entity/utility.js'
import { FastifyInstance } from 'fastify';

export default async function(server: FastifyInstance) {
  await server.orm["typeorm"]
  .createQueryBuilder()
  .insert()
  .into(Utility)
  .values([
    //[ref] in our db [table=instance]
    { id: 0, name: `sample`, description: `sample` },
    
    //set..
    { id: 1, name: `upsert_view_in_mysql`, description: `Update or Create view in mysql` }, //MySQL Does Not Support Materialized Views
    //{ id: , name: ``, description: `` },
    { id: 2, name: `image_proxy`, description: `It can load images from third-party URLs and cache it.` },
    { id: 3, name: `whatsapp_otp`, description: `It can send whatsapp otp` },
    { id: 705, name: `instagram_business`, description: `Instagram Business Commerce — catalog sync, OAuth, Instagram Shop integration via Meta Graph API` },
    { id: 4, name: `llm_provider`, description: `It can work with Google-Ai-Studio(eg - Gemini API), OpenAI-platform(eg - GPT API) etc` },

    { id: 5, name: `code_manager`, description: `It can do update, clone etc task.. on platforms like github` },



    { id: 6, name: `text_classification`, description: `It can train, predict etc.. text-classification models. Text classification is a common NLP task that assigns a label or class to text. [ref=https://huggingface.co/docs/transformers/tasks/sequence_classification]` },


    { id: 7, name: `ai_agent`, description: `It can be used for coding, design etc. by using our [cli] app.` },



    { id: 8, name: `product_engine`, description: `It can be used for Product-Catalogs, Product-list etc. [ref]=https://typesense.org/,https://ecommerce-store.typesense.org/` },




    { id: 9, name: `vibe_coding`, description: `It can be used to generate Prompt-to-Product (P2P) standard — a structured JSON or Markdown format that describes everything needed for an AI coding environment (like Replit, Bolt.new, or v0.dev) to go from an idea → to a complete working product automatically.` },


    

  ])
  .orIgnore()
  .execute();
}
