import setuptools

setuptools.setup(
    name="streamlit_azure_login",
    version="1.0.9",
    author="Thomaz Pougy",
    author_email="tp@rbrasset.com.br",
    description="Componente streamlit para autenticar usuários no azure AD",
    long_description="",
    long_description_content_type="text/plain",
    url="",
    packages=setuptools.find_packages(),
    package_data={"streamlit_azure_login": ["frontend/**/*"]},
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.6",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 0.63",
    ],
)
