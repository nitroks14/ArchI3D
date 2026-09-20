import { useState } from "react";

import type { QuestionnaireState } from "@/domain/model/Question";
import { env } from "@/shared/config/env";

interface QuestionnairePanelProps {
  questionnaire: QuestionnaireState | null;
  onLoadNext: () => void;
  onAnswer: (field: string, value: string) => void;
}

/**
 * Questionnaire IA progressif (moteur a regles V1 - cf backend/app/questionnaire). Le nom de
 * piece est toujours propose par l'IA mais reste editable ici, comme demande.
 */
export function QuestionnairePanel({ questionnaire, onLoadNext, onAnswer }: QuestionnairePanelProps) {
  const [textValue, setTextValue] = useState("");

  if (!questionnaire) {
    return (
      <section className="panel">
        <h2>3. Questionnaire IA</h2>
        <button onClick={onLoadNext}>Charger la prochaine question</button>
      </section>
    );
  }

  if (questionnaire.done || !questionnaire.question) {
    return (
      <section className="panel">
        <h2>3. Questionnaire IA</h2>
        <p>Toutes les questions necessaires ont ete repondues pour l&apos;instant.</p>
        <button onClick={onLoadNext}>Rafraichir</button>
      </section>
    );
  }

  const question = questionnaire.question;

  return (
    <section className="panel">
      <h2>3. Questionnaire IA</h2>
      {question.contextLabel && <p className="hint">Piece concernee : {question.contextLabel}</p>}
      <p className="question-text">{question.text}</p>

      {question.type === "text" && (
        <div className="row">
          <input
            value={textValue}
            onChange={(e) => setTextValue(e.target.value)}
            placeholder="Reponse..."
          />
          <button
            onClick={() => {
              onAnswer(question.field, textValue);
              setTextValue("");
            }}
          >
            Valider
          </button>
        </div>
      )}

      {question.type === "single_choice" && (
        <div className="choice-list">
          {question.options.map((option) => (
            <button key={option.value} onClick={() => onAnswer(question.field, option.value)}>
              {option.label}
            </button>
          ))}
        </div>
      )}

      {question.type === "construction_type_visual" && (
        <div className="catalog-grid">
          {question.options.map((option) => (
            <button
              key={option.value}
              className="catalog-card"
              onClick={() => onAnswer(question.field, option.value)}
            >
              {option.imageUrl && <img src={`${env.apiBaseUrl}${option.imageUrl}`} alt={option.label} />}
              <span>{option.label}</span>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
