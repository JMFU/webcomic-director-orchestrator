# Escribí un Libro con un Equipo Editorial de IA (Y Lo Hizo Todo Solo)

**Subtítulo:** Cómo construí 3 agentes de IA que trabajan juntos como un equipo editorial real: uno imagina, otro estructura, el tercero pule la prosa

---

Un equipo editorial clásico tiene roles claros: alguien piensa en giros creativos, otro asegura que la historia fluya, y hay un editor que pule cada párrafo.

Yo quería eso. Pero no tenía un equipo.

Así que decidí construirlo.

---

## El Problema

Escribir es un proceso multidisciplinar. Cuando escribes una novela, necesitas:

- **Creatividad** para expandir ideas y crear momentos memorables
- **Estructura** para que el ritmo no se derrumbe
- **Estilo** para que la prosa no sea solo texto, sino lectura

Normalmente contratas un consultor, un editor, un ghostwriter. Yo quería ver si podía **delegar eso en agentes de IA** sin perder la voz del autor.

---

## La Solución — El Proyecto

Construí **ia-Escritura**, un sistema multi-agente en Python + Streamlit donde tres agentes especializados colaboran en tiempo real:

**🎯 Estratega Creativo**
Expande ideas, sugiere giros argumentales, profundiza en la psicología de los personajes. Es el que dice "y si el protagonista discovers que...".

**🏗️ Arquitecto de Estructura**
Experto en narrativa (Viaje del Héroe, 3 actos, etc.). Asegura que el ritmo sea correcto y que no haya huecos lógicos en la trama.

**✍️ Editor de Estilo**
Ojo clínico para la prosa. Elimina muletillas, ajusta el tono, mejora vocabulario. Es directo y crítico.

El **secreto del sistema** es el Documento Maestro: un texto compartido que todos los agentes leen antes de responder. Así mantienen coherencia y no se contradicen entre sí.

---

## Los Desafíos

El mayor reto no fue ningún agente individual. Fue **hacer que no se contradijeran**.

¿Cómo asegurar que el Editor no sugiera algo que contradiga lo que escribió el Estratega?

La solución fue incluir en cada prompt una instrucción explícita: *"Verifica que tu respuesta no contradiga lo escrito. Si sugieres algo nuevo, márcalo."*

También: los filtros de seguridad de Gemini bloquean contenido literario válido (suspenso, drama intenso). La solución fue configurar safety settings específicos para contexto creativo, manteniendo la seguridad general.

---

## Resultados y Aprendizajes

El sistema ahora permite:

- **Chatear con 3 agentes especializados** sobre tu texto
- **Subir tu borrador** (PDF o DOCX) para que los agentes lo analicen
- **Exportar/importar proyectos** completos como JSON
- **Mantener coherencia** entre todas las respuestas de IA

**Lo que aprendí:**
- Un sistema multi-agente necesita más que roles diferentes. Necesita **memoria compartida**.
- La mejor IA es la que sabe decir *"no tengo esa información en tu texto"*.
- Los filtros de seguridad son configurables. No es todo o nada.

---

## Reflexión Profesional

Este proyecto me enseñó que **diseñar un equipo de IA no es tan diferente de diseñar un equipo humano**: definir roles claros, asegurar comunicación, y verificar que todos trabajen hacia el mismo objetivo.

Y eso, en un mercado donde cada vez más productos se construyen sobre LLMs, es exactamente el tipo de pensamiento que buscan las empresas.

---

**¿Has usado sistemas multi-agente en tu trabajo? ¿Cómo manejas la coherencia entre agentes?**

🔗 [github.com/JMFU/ia-Escritura](https://github.com/JMFU/ia-Escritura)

Si estás escribiendo algo y quieres probar un enfoque diferente, contáctame. Siempre interesa explorar nuevas formas de collaboration autor-IA.

---

#MultiAgentAI #AIWritingAssistant #GeminiAPI #Streamlit #PromptEngineering #ContentCreation #CreativeWriting #PythonDeveloper