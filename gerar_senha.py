import streamlit_authenticator as stauth

passwords = ["1234"]

hashed_passwords = stauth.Hasher(passwords).generate()

print(hashed_passwords)