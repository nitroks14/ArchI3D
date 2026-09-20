import type { ExtractedMaterial } from "@/domain/model/Project";

export interface MaterialInvoiceRepository {
  extractInvoice(projectId: string, invoiceId: string): Promise<ExtractedMaterial>;
  linkInvoice(projectId: string, invoiceId: string, roomId: string, wallId: string): Promise<void>;
}
