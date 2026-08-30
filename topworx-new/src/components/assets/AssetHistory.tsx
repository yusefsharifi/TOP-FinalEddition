import { List, List.Item } from 'antd';
// فرض: asset.history = [{date, user, action, description}]
<List>
  {asset.history?.map((log, i) => (
    <ListItem key={i}>
      <ListItemText
        primary={`${log.user} - ${log.action}`}
        secondary={`${log.description || ""} (${new Date(log.date).toLocaleString("fa-IR")})`}
      />
    </ListItem>
  ))}
</List>