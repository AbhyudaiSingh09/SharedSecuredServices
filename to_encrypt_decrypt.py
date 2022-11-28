from cryptography.fernet import Fernet


key = b'afzunXOZLJCLRyeGNjRvG16ZUrwwl-zV6HvONVO6q5w='
fernet = Fernet(key)


def to_encrypt_string(to_encrypt):
    byte_to_encrypt = bytes(to_encrypt,'UTF-8')
    encMessage = fernet.encrypt(byte_to_encrypt)
    return encMessage

def to_decrypt_string(byte_to_decrypt):
    decMessage = fernet.decrypt(byte_to_decrypt).decode('UTF-8')
    print(decMessage)
    return decMessage
        
