from agent.AgentConversationChain import AgentConversationChain
from agent.StageAnalyzerChain import StageAnalyzerChain
from typing import Dict, List, Any
from agent.Tools import get_customer, save_conversation
import os
import re

class SalesGPT:
    """Módulo controlado para o agente de vendas."""

    

    def __init__(
        self,
        stage_analyzer_chain: StageAnalyzerChain,
        sales_conversation_utterance_chain: AgentConversationChain,
        verbose: bool = False,
        **kwargs
    ):
        self.internal_chain = None
        self.conversation_history: List[str] = []
        self.current_conversation_stage: str = '1'
        self.stage_analyzer_chain = stage_analyzer_chain
        self.sales_conversation_utterance_chain = sales_conversation_utterance_chain

        self.conversation_stage_dict: Dict = {
        '1' : "1. Introduçãp: Começe a conversa se apresentando e apresentando sua empresa. Seja educado e respeitoso, mas mantenha o tom profissional para a conversa, use o nome do cliente.SEMPRE FINALIZE COMO POSSO TE AJUDAR HOJE ?", 
        '2':  "2. Qualificação: Qualifique o o  tipo de apolice do cliente, confirmando dados para consultar o cliente. Pergunte se ele já possui um seguro e qual o tipo de apolice que ele possui, cpf e placa do carro",
        '3':  "3. Proposição de valor: Com a minha ajuda, o processo de abertura de sinistro será rápido e fácil. Estou aqui para garantir que todas as informações necessárias sejam coletadas corretamente e que seu aviso seja processado sem problemas.",
        '4':  "4. Necessita análise: Antes de iniciarmos, Você poderia me fornecer mais detalhes sobre o incidente? Quando e onde ocorreu? Descreva o que aconteceu e se houve algum dano ao veículo ou a terceiros e solicitar os dados do cleinte como CPF e placa do carro.",
        '5':  "5. Apresentação de Solução: Você poderia me enviar as fotos do seu carro mostrando onde foram as regiões danificadas e fazer o upload aqui mesmo?",
        '6':  "6. Lidar com objeções: Endereçe quaisquer objeções que o prospect possa ter sobre o seu produto/serviço. Esteja preparado para providenciar evidências ou testemunhos para suportar seu discurso.",
        '7':  "7. Fechamento: Agradeça, repsse seu nome. Acho que já tenho todas as informações que preciso. Vou gerar um {{protocolo}} e é importante que você o anote. "}

        # Valores padrão + override por ENV ou kwargs
        self.salesperson_name = kwargs.get("salesperson_name", os.getenv("SALESPERSON_NAME", "Henrique Souza"))
        self.salesperson_role = kwargs.get("salesperson_role", os.getenv("SALESPERSON_ROLE", "Atendente de Seguros"))
        self.company_name = kwargs.get("company_name", os.getenv("COMPANY_NAME", "Capgemini Brasil"))
        self.company_business = kwargs.get("company_business", os.getenv("COMPANY_BUSINESS", "Serviços de TI, Consultoria e Outsourcing, com foco em transformação digital."))
        self.company_values = kwargs.get("company_values", os.getenv("COMPANY_VALUES", "Inovação, Colaboração, Diversidade e Sustentabilidade."))
        self.conversation_purpose = kwargs.get("conversation_purpose", os.getenv("CONVERSATION_PURPOSE", "Vender serviços de TI., Consultoria e Outsourcing., Digitalizar para transformar."))
        self.conversation_type = kwargs.get("conversation_type", "chat")
        self.verbose = verbose
        self.client_data = {
            "cpf": None,
            "placa": None
        }

    def retrieve_conversation_stage(self, key):
        return self.conversation_stage_dict.get(key, '1')

    def seed_agent(self):
        self.current_conversation_stage = self.retrieve_conversation_stage('1')
        self.conversation_history = []

    def determine_conversation_stage(self):
        conversation_stage_id = self.stage_analyzer_chain.run(
            conversation_history='\n'.join(self.conversation_history),
            current_conversation_stage=self.current_conversation_stage
        )
        
        self.current_conversation_stage = self.retrieve_conversation_stage(conversation_stage_id)
        print(f"Estágio da Conversa: {self.current_conversation_stage}")
        return f"Estágio da Conversa: {self.current_conversation_stage}"

    def human_step(self, human_input, session_id: str = None):
        self.conversation_history.append(human_input + '<END_OF_TURN>')
        
        # Captura simples de CPF (formato com ou sem pontos e traço)
        cpf_match = re.search(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', human_input)
        if cpf_match:
            self.client_data["cpf"] = cpf_match.group()
        
        # Captura simples de placa (ex: ABC1D23 ou ABC-1234)
        placa_match = re.search(r'\b[A-Z]{3}-?\d{1}[A-Z0-9]{1}\d{2}\b', human_input, re.IGNORECASE)
        if placa_match:
            self.client_data["placa"] = placa_match.group().upper()
        
        # Se tiver CPF e placa, busca o cliente
        if self.client_data["cpf"] and self.client_data["placa"]:
            result = get_customer(self.client_data["cpf"], self.client_data["placa"])
            print("[TOOL] Dados do cliente:", result)

        self.executar_tool_por_estagio(self.salesperson_name, session_id, human_input, False)

    def step(self, session_id: str = None) -> str:
        return self._call(inputs={}, session_id=session_id)
    
    def executar_tool_por_estagio(self, user: str, session_id: str, ultimo_input: str, user_input: bool = False):
        print(f"Executando ferramenta por estágio: {self.current_conversation_stage}")
        print(f"Último input: {ultimo_input}")
        stage = self.current_conversation_stage[:1]
        role = "user" if user_input else "assistant"
        save_conversation(session_id, role, ultimo_input, user, stage)

        if stage == '4':  # Necessita análise
            resultado = get_customer(user)
            print("[TOOL] Resultado da busca:", resultado)
        elif stage == '7':  # Fechamento
            ultimo_input = self.conversation_history[-2] if len(self.conversation_history) > 1 else ''


    def _call(self, inputs: Dict[str, Any], session_id: str = None) -> str:
        ai_message = self.sales_conversation_utterance_chain.run(
            salesperson_name=self.salesperson_name,
            salesperson_role=self.salesperson_role,
            company_name=self.company_name,
            company_business=self.company_business,
            company_values=self.company_values,
            conversation_purpose=self.conversation_purpose,
            conversation_history="\n".join(self.conversation_history),
            conversation_stage=self.current_conversation_stage,
            conversation_type=self.conversation_type
        )
        self.conversation_history.append(ai_message)
        resultMessage = f"{self.salesperson_name}: {ai_message.rstrip('<END_OF_TURN>')}"
        print(resultMessage)
        self.executar_tool_por_estagio(self.salesperson_name, session_id, resultMessage, False)
        return resultMessage

    

    @classmethod
    def from_llm(cls, llm, verbose: bool = False, **kwargs):
        stage_analyzer_chain = StageAnalyzerChain.from_llm(llm, verbose=verbose)
        conversation_utterance_chain = AgentConversationChain.from_llm(llm, verbose=verbose)
        return cls(stage_analyzer_chain, conversation_utterance_chain, verbose=verbose, **kwargs)

    
            