from traceback import print_exception
from rich.logging import RichHandler
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from git_loader import GitDocumentLoader


from dotenv import load_dotenv
import os


class GitInterpreter:
    SUMMARIZE_TEMPLATE = """Summarize the changes made in this commit. {text}
    CONCISE SUMMARY:"""
    REFINE_TEMPLATE = (
        "Your job is to interpret and summarize the changes made in a list of commits."
        "The text generated should use a formal, technical, but concise and simople style."
        "The text should use a first person plural pronoun (we) to refer to the team or the project."
        "Don't provide specific dates or timestamp, neither path of the files, instead interpret the hours worked or the files changed."
        "If the amount of changes is represent the work done for one day, use paragraph or more for the final text. If not, use a sentence or two."
        "We have provided an existing summary up to a certain point: {existing_answer}\n"
        "We have the opportunity to refine the existing summary"
        "(only if needed) with some more context below.\n"
        "------------\n"
        "{text}\n"
        "------------\n"
        "Given the new context, refine the original summary"
        "If the context isn't useful, return the original summary."
    )

    def __init__(self, json_path, verbose=False) -> None:
        load_dotenv()
        FORMAT = "%(message)s"
        if verbose:
            logging.basicConfig(
                level="DEBUG", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
            )
        else:
            logging.basicConfig(
                level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
            )
        self.log = logging.getLogger("rich")
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o", temperature=0.1
        )
        self.loader = GitDocumentLoader(file_path=json_path)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=150,
            length_function=len,
            separators=[
                "\n\n",
                "\n",
                " ",
                ".",
                ",",
                "\u200b",  # Zero-width space
                "\uff0c",  # Fullwidth comma
                "\u3001",  # Ideographic comma
                "\uff0e",  # Fullwidth full stop
                "\u3002",  # Ideographic full stop
                "",
            ],
        )
        self.json_path = json_path
        self.prompt = PromptTemplate.from_template(self.SUMMARIZE_TEMPLATE)
        self.refine_prompt = PromptTemplate.from_template(self.REFINE_TEMPLATE)

    def interpret_commits(self):
        try:
            docs = self.loader.load()
            if not docs:
                return -1
            self.log.info(f"Loaded {len(docs)} documents from {self.json_path}")
            branches = set([doc.metadata["branch"] for doc in docs])
            branch_results = []
            for branch in branches:
                self.log.info(f"Interpreting branch: {branch}")
                docs_branch = [doc for doc in docs if doc.metadata["branch"] == branch]
                splits = self.splitter.split_documents(docs_branch)
                chain = load_summarize_chain(
                    llm=self.llm,
                    chain_type="refine",
                    question_prompt=self.prompt,
                    refine_prompt=self.refine_prompt,
                    return_intermediate_steps=True,
                    input_key="input_documents",
                    output_key="output_text",
                )
                result = {branch: chain({"input_documents": splits}, return_only_outputs=True)["output_text"]}
                branch_results.append(result)
            return branch_results
        except Exception as e:
            self.log.error(e)
            print_exception(e)
            return -1
