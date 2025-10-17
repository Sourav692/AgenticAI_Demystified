def transform_query(state):
    question = state["question"]
    rephrased_question = question_rewriter.invoke({"question": question})
    return {"question": rephrased_question, "documents": state["documents"]}
