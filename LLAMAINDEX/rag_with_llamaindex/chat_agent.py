# REPLACE THIS WITH YOUR CODE

index = None


@cl.on_chat_start
async def on_chat_start():
    global index
    # Settings
    settings = await cl.ChatSettings(
        [
            Select(
                id= # REPLACE THIS WITH YOUR CODE
                label= # REPLACE THIS WITH YOUR CODE
                values=# REPLACE THIS WITH YOUR CODE
                initial_index=0,
            ),
            
            # REPLACE THIS WITH YOUR CODE,
        ]
    ).send()


def wikisearch_engine(index):
    query_engine = # REPLACE THIS WITH YOUR CODE
    return query_engine


def create_react_agent(MODEL):
    query_engine_tools = [
        QueryEngineTool(
            # REPLACE THIS WITH YOUR CODE
            ),
        )
    ]

    openai.api_key = # REPLACE THIS WITH YOUR CODE
    llm = # REPLACE THIS WITH YOUR CODE
    agent = # REPLACE THIS WITH YOUR CODE
    return agent


@cl.on_settings_update
async def setup_agent(settings):
    global agent
    global index
    query = # REPLACE THIS WITH YOUR CODE
    index = # REPLACE THIS WITH YOUR CODE

    print("on_settings_update", settings)
    MODEL = # REPLACE THIS WITH YOUR CODE
    agent = # REPLACE THIS WITH YOUR CODE
    await cl.Message(
        author="Agent", content=f"""Wikipage(s) "{query}" successfully indexed"""
    ).send()


@cl.on_message
async def main(message: str):
    if agent:
        response = # REPLACE THIS WITH YOUR CODE
        await cl.Message(author="Agent", content=response).send()
