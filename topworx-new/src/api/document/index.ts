import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { Document, DocumentFolder, DocumentVersion, DocumentComment, DocumentShare, DocumentTemplate, DocumentWorkflow, DocumentAudit, DocumentSearch } from '../../types/document';

// --- Documents ---
export const useDocuments = (filter?: any) =>
  useQuery<Document[]>(['documents', filter], async () => {
    const { data } = await axios.get('/api/documents', { params: filter });
    return data;
  });

export const useCreateDocument = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: FormData) => axios.post('/api/documents', payload, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    {
      onSuccess: () => queryClient.invalidateQueries(['documents'])
    }
  );
};

export const useUpdateDocument = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Document>) => axios.put(`/api/documents/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['documents'])
    }
  );
};

export const useDeleteDocument = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/documents/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['documents'])
    }
  );
};

// --- Document Search ---
export const useDocumentSearch = (searchParams: DocumentSearch) =>
  useQuery(['documentSearch', searchParams], async () => {
    const { data } = await axios.post('/api/documents/search', searchParams);
    return data;
  });

// --- Document Folders ---
export const useDocumentFolders = (filter?: any) =>
  useQuery<DocumentFolder[]>(['documentFolders', filter], async () => {
    const { data } = await axios.get('/api/documents/folders', { params: filter });
    return data;
  });

export const useCreateDocumentFolder = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<DocumentFolder>) => axios.post('/api/documents/folders', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['documentFolders'])
    }
  );
};

export const useUpdateDocumentFolder = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<DocumentFolder>) => axios.put(`/api/documents/folders/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['documentFolders'])
    }
  );
};

export const useDeleteDocumentFolder = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/documents/folders/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['documentFolders'])
    }
  );
};

// --- Document Versions ---
export const useDocumentVersions = (documentId: number) =>
  useQuery(['documentVersions', documentId], async () => {
    const { data } = await axios.get(`/api/documents/${documentId}/versions`);
    return data;
  });

export const useCreateDocumentVersion = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: { documentId: number; file: File; changes: string }) => {
      const formData = new FormData();
      formData.append('file', payload.file);
      formData.append('changes', payload.changes);
      return axios.post(`/api/documents/${payload.documentId}/versions`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    },
    {
      onSuccess: () => queryClient.invalidateQueries(['documentVersions'])
    }
  );
};

// --- Document Comments ---
export const useDocumentComments = (documentId: number) =>
  useQuery(['documentComments', documentId], async () => {
    const { data } = await axios.get(`/api/documents/${documentId}/comments`);
    return data;
  });

export const useCreateDocumentComment = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<DocumentComment>) => axios.post(`/api/documents/${payload.documentId}/comments`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['documentComments'])
    }
  );
};

export const useUpdateDocumentComment = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<DocumentComment>) => axios.put(`/api/documents/comments/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['documentComments'])
    }
  );
};

export const useDeleteDocumentComment = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/documents/comments/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['documentComments'])
    }
  );
};

// --- Document Shares ---
export const useDocumentShares = (documentId: number) =>
  useQuery(['documentShares', documentId], async () => {
    const { data } = await axios.get(`/api/documents/${documentId}/shares`);
    return data;
  });

export const useCreateDocumentShare = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<DocumentShare>) => axios.post(`/api/documents/${payload.documentId}/shares`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['documentShares'])
    }
  );
};

export const useUpdateDocumentShare = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<DocumentShare>) => axios.put(`/api/documents/shares/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['documentShares'])
    }
  );
};

export const useDeleteDocumentShare = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/documents/shares/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['documentShares'])
    }
  );
};

// --- Document Templates ---
export const useDocumentTemplates = (filter?: any) =>
  useQuery<DocumentTemplate[]>(['documentTemplates', filter], async () => {
    const { data } = await axios.get('/api/documents/templates', { params: filter });
    return data;
  });

export const useCreateDocumentTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<DocumentTemplate>) => axios.post('/api/documents/templates', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['documentTemplates'])
    }
  );
};

export const useUpdateDocumentTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<DocumentTemplate>) => axios.put(`/api/documents/templates/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['documentTemplates'])
    }
  );
};

export const useDeleteDocumentTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/documents/templates/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['documentTemplates'])
    }
  );
};

// --- Document Workflows ---
export const useDocumentWorkflows = (filter?: any) =>
  useQuery<DocumentWorkflow[]>(['documentWorkflows', filter], async () => {
    const { data } = await axios.get('/api/documents/workflows', { params: filter });
    return data;
  });

export const useCreateDocumentWorkflow = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<DocumentWorkflow>) => axios.post('/api/documents/workflows', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['documentWorkflows'])
    }
  );
};

export const useUpdateDocumentWorkflow = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<DocumentWorkflow>) => axios.put(`/api/documents/workflows/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['documentWorkflows'])
    }
  );
};

export const useDeleteDocumentWorkflow = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/documents/workflows/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['documentWorkflows'])
    }
  );
};

// --- Document Audits ---
export const useDocumentAudits = (filter?: any) =>
  useQuery<DocumentAudit[]>(['documentAudits', filter], async () => {
    const { data } = await axios.get('/api/documents/audits', { params: filter });
    return data;
  });

// --- Document Dashboard ---
export const useDocumentDashboard = () =>
  useQuery(['documentDashboard'], async () => {
    const { data } = await axios.get('/api/documents/dashboard');
    return data;
  }); 