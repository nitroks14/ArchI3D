import type { MaterialInvoiceRepository } from "@/domain/repositories/MaterialInvoiceRepository";
import type { ExtractedMaterial } from "@/domain/model/Project";
import { apiClient } from "@/infrastructure/http/ApiClient";

export class HttpMaterialInvoiceRepository implements MaterialInvoiceRepository {
  extractInvoice(projectId: string, invoiceId: string): Promise<ExtractedMaterial> {
    return apiClient.postJson<ExtractedMaterial>(
      `/projects/${projectId}/invoices/${invoiceId}/extract`,
      {},
    );
  }

  async linkInvoice(projectId: string, invoiceId: string, roomId: string, wallId: string): Promise<void> {
    await apiClient.postJson(`/projects/${projectId}/invoices/${invoiceId}/link`, {
      roomId,
      wallId,
    });
  }
}
