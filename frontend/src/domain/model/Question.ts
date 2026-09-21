export interface QuestionOption {
  value: string;
  label: string;
  imageUrl: string | null;
}

export interface Question {
  id: string;
  field: string;
  text: string;
  type: "text" | "single_choice" | "construction_type_visual";
  options: QuestionOption[];
  contextLabel: string | null;
  /**
   * Pre-remplissage intelligent (cf backend/app/wall_profiles) : une SUGGESTION issue d'un profil
   * deja utilise ailleurs dans le projet - jamais une valeur validee automatiquement. Toujours
   * modifiable/rejetable : les autres options restent cliquables normalement.
   */
  suggestedValue: string | null;
  suggestionNote: string | null;
}

export interface QuestionnaireState {
  done: boolean;
  question: Question | null;
}
