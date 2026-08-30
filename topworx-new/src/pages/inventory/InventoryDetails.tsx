import { List, List.Item } from 'antd';
// فرض: item.history = [{date, user, action, quantity, description}]
<List>
  {item.history?.map((log, i) => (
    <ListItem key={i}>
      <ListItemText
        primary={`${log.user} - ${log.action} (${log.quantity})`}
        secondary={`${log.description || ""} (${new Date(log.date).toLocaleString("fa-IR")})`}
      />
    </ListItem>
  ))}
</List>