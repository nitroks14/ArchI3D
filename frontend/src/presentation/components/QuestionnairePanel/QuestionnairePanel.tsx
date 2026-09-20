import { useState } from "react";

import type { QuestionnaireState } from "@/domain/model/Question";
import { env } from "@/shared/config/env";
import { Button } from "@/presentation/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/presentation/components/ui/card";
import { Input } from "@/presentation/components/ui/input";

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
      <Card>
        <CardHeader>
          <CardTitle>3. Questionnaire IA</CardTitle>
        </CardHeader>
        <CardContent>
          <Button onClick={onLoadNext}>Charger la prochaine question</Button>
        </CardContent>
      </Card>
    );
  }

  if (questionnaire.done || !questionnaire.question) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>3. Questionnaire IA</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <p className="text-sm text-muted-foreground">
            Toutes les questions necessaires ont ete repondues pour l&apos;instant.
          </p>
          <Button variant="outline" onClick={onLoadNext}>
            Rafraichir
          </Button>
        </CardContent>
      </Card>
    );
  }

  const question = questionnaire.question;

  return (
    <Card>
      <CardHeader>
        <CardTitle>3. Questionnaire IA</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        {question.contextLabel && (
          <p className="text-sm text-muted-foreground">Piece concernee : {question.contextLabel}</p>
        )}
        <p className="font-medium">{question.text}</p>

        {question.type === "text" && (
          <div className="flex flex-wrap items-center gap-2">
            <Input
              className="w-64"
              value={textValue}
              onChange={(e) => setTextValue(e.target.value)}
              placeholder="Reponse..."
            />
            <Button
              onClick={() => {
                onAnswer(question.field, textValue);
                setTextValue("");
              }}
            >
              Valider
            </Button>
          </div>
        )}

        {question.type === "single_choice" && (
          <div className="flex flex-wrap gap-2">
            {question.options.map((option) => (
              <Button key={option.value} variant="outline" onClick={() => onAnswer(question.field, option.value)}>
                {option.label}
              </Button>
            ))}
          </div>
        )}

        {question.type === "construction_type_visual" && (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
            {question.options.map((option) => (
              <button
                key={option.value}
                className="flex flex-col items-center gap-1.5 rounded-md border bg-card p-2 text-center text-sm shadow-sm transition-colors hover:border-primary hover:bg-accent"
                onClick={() => onAnswer(question.field, option.value)}
              >
                {option.imageUrl && (
                  <img
                    src={`${env.apiBaseUrl}${option.imageUrl}`}
                    alt={option.label}
                    className="w-full rounded"
                  />
                )}
                <span>{option.label}</span>
              </button>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
