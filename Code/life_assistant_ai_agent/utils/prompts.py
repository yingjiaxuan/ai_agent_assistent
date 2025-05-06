# Store all prompt templates here
def get_prompt_for_question(question):
    return f"Answer the following question: {question}"

def get_prompt_for_memory_enhanced_question(question, memory):
    return f"Based on the previous interactions: {memory}, answer the following question: {question}"