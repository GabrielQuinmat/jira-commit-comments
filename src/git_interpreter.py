from rich.logging import RichHandler
import logging
from langchain_community.document_loaders import JSONLoader
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
        'Your job is to produce a final summary of the work done given some commit data\n'
        'We have provided an existing summary up to a certain point: {existing_answer}\n'
        'We have the opportunity to refine the existing summary'
        '(only if needed) with some more context below.\n'
        '------------\n'
        '{text}\n'
        '------------\n'
        'Given the new context, refine the original summary in Italian'
        "If the context isn't useful, return the original summary."
    )

    def __init__(self, verbose, json_path) -> None:
        load_dotenv()
        FORMAT = '%(message)s'
        if verbose:
            logging.basicConfig(
                level='DEBUG', format=FORMAT, datefmt='[%X]', handlers=[RichHandler()]
            )
        else:
            logging.basicConfig(
                level='INFO', format=FORMAT, datefmt='[%X]', handlers=[RichHandler()]
            )
        self.log = logging.getLogger('rich')
        self.llm = ChatOpenAI(api_key=os.getenv('OPENAI_API_KEY'), model='gpt-4', temperature=0.3)
        self.loader = GitDocumentLoader(file_path=json_path)
        self.prompt = PromptTemplate.from_template(self.SUMMARIZE_TEMPLATE)
        self.refine_prompt = PromptTemplate.from_template(self.REFINE_TEMPLATE)

    def interpret_commits(self):
        docs = self.loader.load()
        chain = load_summarize_chain(
            llm=self.llm,
            chain_type='refine',
            question_prompt=self.prompt,
            refine_prompt=self.refine_prompt,
            return_intermediate_steps=True,
            input_key='input_documents',
            output_key='output_text',
        )
        result = chain({'input_documents': docs}, return_only_outputs=True)
        return result