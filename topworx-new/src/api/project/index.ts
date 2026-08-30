import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { Project, Task, Milestone, TimeEntry, ProjectReport, ProjectTemplate } from '../../types/project';

// --- Projects ---
export const useProjects = (filter?: any) =>
  useQuery<Project[]>(['projects', filter], async () => {
    const { data } = await axios.get('/api/projects', { params: filter });
    return data;
  });

export const useCreateProject = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Project>) => axios.post('/api/projects', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['projects'])
    }
  );
};

export const useUpdateProject = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Project>) => axios.put(`/api/projects/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['projects'])
    }
  );
};

export const useDeleteProject = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/projects/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['projects'])
    }
  );
};

// --- Tasks ---
export const useTasks = (filter?: any) =>
  useQuery<Task[]>(['tasks', filter], async () => {
    const { data } = await axios.get('/api/projects/tasks', { params: filter });
    return data;
  });

export const useCreateTask = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Task>) => axios.post('/api/projects/tasks', payload),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['tasks']);
        queryClient.invalidateQueries(['projects']);
      }
    }
  );
};

export const useUpdateTask = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Task>) => axios.put(`/api/projects/tasks/${payload.id}`, payload),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['tasks']);
        queryClient.invalidateQueries(['projects']);
      }
    }
  );
};

export const useDeleteTask = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/projects/tasks/${id}`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['tasks']);
        queryClient.invalidateQueries(['projects']);
      }
    }
  );
};

// --- Milestones ---
export const useMilestones = (filter?: any) =>
  useQuery<Milestone[]>(['milestones', filter], async () => {
    const { data } = await axios.get('/api/projects/milestones', { params: filter });
    return data;
  });

export const useCreateMilestone = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Milestone>) => axios.post('/api/projects/milestones', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['milestones'])
    }
  );
};

export const useUpdateMilestone = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<Milestone>) => axios.put(`/api/projects/milestones/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['milestones'])
    }
  );
};

export const useDeleteMilestone = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/projects/milestones/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['milestones'])
    }
  );
};

// --- Time Entries ---
export const useTimeEntries = (filter?: any) =>
  useQuery<TimeEntry[]>(['timeEntries', filter], async () => {
    const { data } = await axios.get('/api/projects/time-entries', { params: filter });
    return data;
  });

export const useCreateTimeEntry = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<TimeEntry>) => axios.post('/api/projects/time-entries', payload),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['timeEntries']);
        queryClient.invalidateQueries(['projects']);
      }
    }
  );
};

export const useUpdateTimeEntry = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<TimeEntry>) => axios.put(`/api/projects/time-entries/${payload.id}`, payload),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['timeEntries']);
        queryClient.invalidateQueries(['projects']);
      }
    }
  );
};

export const useDeleteTimeEntry = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/projects/time-entries/${id}`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['timeEntries']);
        queryClient.invalidateQueries(['projects']);
      }
    }
  );
};

// --- Project Reports ---
export const useProjectReports = (filter?: any) =>
  useQuery<ProjectReport[]>(['projectReports', filter], async () => {
    const { data } = await axios.get('/api/projects/reports', { params: filter });
    return data;
  });

export const useCreateProjectReport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<ProjectReport>) => axios.post('/api/projects/reports', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['projectReports'])
    }
  );
};

export const useUpdateProjectReport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<ProjectReport>) => axios.put(`/api/projects/reports/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['projectReports'])
    }
  );
};

export const useDeleteProjectReport = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/projects/reports/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['projectReports'])
    }
  );
};

// --- Project Templates ---
export const useProjectTemplates = (filter?: any) =>
  useQuery<ProjectTemplate[]>(['projectTemplates', filter], async () => {
    const { data } = await axios.get('/api/projects/templates', { params: filter });
    return data;
  });

export const useCreateProjectTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<ProjectTemplate>) => axios.post('/api/projects/templates', payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['projectTemplates'])
    }
  );
};

export const useUpdateProjectTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (payload: Partial<ProjectTemplate>) => axios.put(`/api/projects/templates/${payload.id}`, payload),
    {
      onSuccess: () => queryClient.invalidateQueries(['projectTemplates'])
    }
  );
};

export const useDeleteProjectTemplate = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (id: number) => axios.delete(`/api/projects/templates/${id}`),
    {
      onSuccess: () => queryClient.invalidateQueries(['projectTemplates'])
    }
  );
};

// --- Project Dashboard ---
export const useProjectDashboard = () =>
  useQuery(['projectDashboard'], async () => {
    const { data } = await axios.get('/api/projects/dashboard');
    return data;
  });