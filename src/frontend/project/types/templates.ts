export interface Template {
  template_id: string;
  name: string;
  description?: string;
  template_image_url?: string;
  parameters: TemplateParameter[];
}

export interface TemplateParameter {
  name: string;
  value: {
    value: string;
    label?: string;
  };
}

export interface CachedTemplateData {
  templates: Template[];
  timestamp: number;
}