import { Progress, Typography } from 'antd';
import { List, List.Item } from 'antd';

// فرض: budget.history = [{date, user, action, description}]
<List>
  {budget.history?.map((log, i) => (
    <ListItem key={i}>
      <ListItemText
        primary={`${log.user} - ${log.action}`}
        secondary={`${log.description || ""} (${new Date(log.date).toLocaleString("fa-IR")})`}
      />
    </ListItem>
  ))}
</List>

<Button onClick={approveBudget}>تأیید بودجه</Button>

const deviation = ((budget.spent - budget.amount) / budget.amount) * 100;

<div>
  <Typography fontSize={13} color={deviation > 0 ? "error.main" : "success.main"}>
    انحراف بودجه: {deviation.toFixed(1)}%
  </Typography>
  <LinearProgress
    variant="determinate"
    value={Math.min(100, (budget.spent / budget.amount) * 100)}
    color={budget.spent > budget.amount ? "error" : "primary"}
    style={{  height: 8, borderRadius: 2, mt: 1  }}
  />
</div>