import type { MaterialInvoiceRepository } from "@/domain/repositories/MaterialInvoiceRepository";

export const manageMaterialInvoice = (repo: MaterialInvoiceRepository) => ({
  extract: (projectId: string, invoiceId: string) => repo.extractInvoice(projectId, invoiceId),
  link: (projectId: string, invoiceId: string, roomId: string, wallId: string) =>
    repo.linkInvoice(projectId, invoiceId, roomId, wallId),
});
