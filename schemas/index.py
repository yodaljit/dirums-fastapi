def SerailizerDict(a) -> dict:
    return {**{i:str(a[i]) for i in a if i=='_id'}, **{i:a[i] for i in a if i!='_id'}}

def serializerList(entity) -> list:
    return [SerailizerDict(item) for item in entity]