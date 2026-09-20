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
}

export interface QuestionnaireState {
  done: boolean;
  question: Question | null;
}
