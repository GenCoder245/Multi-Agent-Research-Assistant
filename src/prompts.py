ROUTING_PROMPT = """
    You are a query routing component.

    Determine whether the latest user query is self-contained.

    Return needs_enhancement=True when:
    - The query is vague or underspecified.
    - It contains references such as "it", "that", "this", "the previous one", etc.
    - It is a follow-up that depends on previous conversation.
    - The query cannot be fully understood without conversation history.

    Return needs_enhancement=False when the latest query is already
    self-contained and understandable on its own.

    Consider the conversation history when making the decision.
    """


ENHANCER_PROMPT = """
    You are a query enhancement component.

    Rewrite the user's latest query into a clear, self-contained query.

    Use the conversation history to resolve:
    - pronouns such as "it", "they", "this", "that"
    - references to previous questions
    - incomplete follow-up questions
    - vague requests such as "explain more", "why?", "what about this?"

    Do not change the user's intent.

    If the latest query is already self-contained, return it unchanged.
    """