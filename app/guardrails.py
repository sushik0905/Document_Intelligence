def validate(results, threshold=0.60):
    if not results:
        return False

    # check similarity score
    if results[0]["score"] < threshold:
        return False

    return True
