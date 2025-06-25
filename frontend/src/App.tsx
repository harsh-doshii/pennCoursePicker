import React, { useState } from "react";
import {
  Container,
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  CircularProgress,
  ThemeProvider,
  createTheme,
  CssBaseline,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
} from "@mui/material";
import {
  Search as SearchIcon,
  School as SchoolIcon,
  Comment as CommentIcon,
} from "@mui/icons-material";
import axios from "axios";
import "@fontsource/poppins";
import "@fontsource/roboto-mono";
import ReactMarkdown from "react-markdown";

// Create a theme instance
const theme = createTheme({
  palette: {
    primary: {
      main: "#6C63FF", // Vibrant purple
      light: "#8F88FF",
      dark: "#4A43D9",
    },
    secondary: {
      main: "#FF6584", // Coral pink
      light: "#FF8BA3",
      dark: "#E64A6F",
    },
    background: {
      default: "#F8F9FF",
      paper: "#FFFFFF",
    },
    text: {
      primary: "#2D3142",
      secondary: "#4F5665",
    },
  },
  typography: {
    fontFamily: "'Poppins', sans-serif",
    h1: {
      fontWeight: 700,
      fontSize: "3.5rem",
      background: "linear-gradient(45deg, #6C63FF 30%, #FF6584 90%)",
      WebkitBackgroundClip: "text",
      WebkitTextFillColor: "transparent",
      textShadow: "2px 2px 4px rgba(0,0,0,0.1)",
    },
    h2: {
      fontWeight: 600,
      fontSize: "2rem",
    },
    h5: {
      fontWeight: 600,
      fontSize: "1.5rem",
    },
    body1: {
      fontFamily: "'Roboto Mono', monospace",
      fontSize: "1rem",
      lineHeight: 1.7,
    },
    body2: {
      fontFamily: "'Roboto Mono', monospace",
      fontSize: "0.9rem",
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: "0 4px 20px rgba(0,0,0,0.05)",
          transition: "transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out",
          "&:hover": {
            transform: "translateY(-4px)",
            boxShadow: "0 8px 30px rgba(0,0,0,0.1)",
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          textTransform: "none",
          fontWeight: 600,
          padding: "10px 24px",
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            borderRadius: 12,
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
        },
      },
    },
  },
});

interface CourseInsight {
  summary: string;
  prerequisites_analysis: string;
  difficulty_assessment: string;
  recommendations: string[];
}

interface RedditComment {
  author: string;
  body: string;
  score: number;
  created_utc: number;
}

interface CourseInfo {
  course_code: string;
  title: string;
  description: string;
  prerequisites: string | null;
  reddit_comments: RedditComment[];
}

function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [courseInfo, setCourseInfo] = useState<CourseInfo | null>(null);
  const [insight, setInsight] = useState<CourseInsight | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setCourseInfo(null);
    setInsight(null);

    try {
      // Extract course code from query
      const courseCode = query.match(/CIS\s*\d{4}/i)?.[0].toUpperCase();
      if (!courseCode) {
        throw new Error("Please enter a valid course code (e.g., CIS 5500)");
      }

      // First, get course information
      const courseResponse = await axios.get(
        `http://localhost:8000/api/courses/${courseCode}`
      );
      setCourseInfo(courseResponse.data);

      // Then, get insights
      const insightResponse = await axios.post(
        "http://localhost:8000/api/planning/analyze",
        {
          query,
          course_info: courseResponse.data,
          reddit_comments: courseResponse.data.reddit_comments,
        }
      );

      setInsight(insightResponse.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString();
  };

  const formatPrerequisites = (text: string) => {
    // Split the text into sections based on numbered points
    const sections = text.split(/\d+\.\s+/);

    // Remove empty sections and format each section
    return sections
      .filter((section) => section.trim())
      .map((section, index) => {
        // Extract the title and content
        const [title, ...contentParts] = section.split(/\*\*:\s*/);
        const content = contentParts.join(": ").trim();

        return (
          <Box key={index} sx={{ mb: 3 }}>
            <Typography
              variant="h6"
              color="primary"
              sx={{
                fontWeight: 600,
                mb: 1,
                fontSize: "1.1rem",
              }}
            >
              {title}
            </Typography>
            <Box
              sx={{
                "& p": {
                  margin: 0,
                  lineHeight: 1.8,
                },
                "& strong": {
                  color: "primary.main",
                  fontWeight: 600,
                },
              }}
            >
              <ReactMarkdown>{content}</ReactMarkdown>
            </Box>
          </Box>
        );
      });
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: "100vh",
          background: "linear-gradient(135deg, #F8F9FF 0%, #E8E9FF 100%)",
          py: 4,
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ my: 4 }}>
            <Typography
              variant="h1"
              component="h1"
              gutterBottom
              align="center"
              sx={{ mb: 6 }}
            >
              PennCoursePicker
            </Typography>

            <Paper
              elevation={3}
              sx={{
                p: 4,
                mb: 4,
                borderRadius: 4,
                background: "rgba(255, 255, 255, 0.9)",
                backdropFilter: "blur(10px)",
              }}
            >
              <form onSubmit={handleSubmit}>
                <Box sx={{ display: "flex", gap: 2 }}>
                  <TextField
                    fullWidth
                    label="What do you want to know about a course?"
                    variant="outlined"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g., What do I need to know before taking CIS 5500?"
                    sx={{
                      flexGrow: 1,
                      "& .MuiOutlinedInput-root": {
                        "&:hover fieldset": {
                          borderColor: "primary.light",
                        },
                      },
                    }}
                  />
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={loading}
                    startIcon={
                      loading ? (
                        <CircularProgress size={20} color="inherit" />
                      ) : (
                        <SearchIcon />
                      )
                    }
                    sx={{
                      background:
                        "linear-gradient(45deg, #6C63FF 30%, #FF6584 90%)",
                      "&:hover": {
                        background:
                          "linear-gradient(45deg, #4A43D9 30%, #E64A6F 90%)",
                      },
                    }}
                  >
                    Search
                  </Button>
                </Box>
              </form>
            </Paper>

            {error && (
              <Alert
                severity="error"
                sx={{
                  mb: 4,
                  borderRadius: 2,
                  "& .MuiAlert-icon": {
                    color: "secondary.main",
                  },
                }}
              >
                {error}
              </Alert>
            )}

            {courseInfo && (
              <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                      <SchoolIcon
                        sx={{
                          mr: 1,
                          color: "primary.main",
                          fontSize: "2rem",
                        }}
                      />
                      <Typography variant="h5" component="h2">
                        {courseInfo.course_code}: {courseInfo.title}
                      </Typography>
                    </Box>
                    <Typography variant="body1" paragraph>
                      {courseInfo.description}
                    </Typography>
                    {courseInfo.prerequisites && (
                      <Box sx={{ mt: 3 }}>
                        <Typography
                          variant="h6"
                          color="primary"
                          gutterBottom
                          sx={{
                            fontWeight: 600,
                            fontSize: "1.2rem",
                            mb: 2,
                          }}
                        >
                          Prerequisites
                        </Typography>
                        <Box
                          sx={{
                            pl: 2,
                            borderLeft: "4px solid",
                            borderColor: "primary.light",
                            backgroundColor: "rgba(108, 99, 255, 0.05)",
                            p: 2,
                            borderRadius: "0 8px 8px 0",
                          }}
                        >
                          {formatPrerequisites(courseInfo.prerequisites)}
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                </Card>

                {courseInfo.reddit_comments &&
                  courseInfo.reddit_comments.length > 0 && (
                    <Card>
                      <CardContent>
                        <Box
                          sx={{ display: "flex", alignItems: "center", mb: 2 }}
                        >
                          <CommentIcon
                            sx={{
                              mr: 1,
                              color: "secondary.main",
                              fontSize: "2rem",
                            }}
                          />
                          <Typography variant="h5" component="h2">
                            Student Comments
                          </Typography>
                        </Box>
                        <List>
                          {courseInfo.reddit_comments.map((comment, index) => (
                            <React.Fragment key={index}>
                              <ListItem alignItems="flex-start">
                                <ListItemText
                                  primary={
                                    <Box
                                      sx={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: 1,
                                      }}
                                    >
                                      <Typography
                                        component="span"
                                        variant="subtitle1"
                                        sx={{ fontWeight: 600 }}
                                      >
                                        u/{comment.author}
                                      </Typography>
                                      <Chip
                                        size="small"
                                        label={`Score: ${comment.score}`}
                                        color="primary"
                                        variant="outlined"
                                        sx={{
                                          background: "rgba(108, 99, 255, 0.1)",
                                        }}
                                      />
                                      <Typography
                                        variant="caption"
                                        color="text.secondary"
                                      >
                                        {formatDate(comment.created_utc)}
                                      </Typography>
                                    </Box>
                                  }
                                  secondary={comment.body}
                                />
                              </ListItem>
                              {index <
                                courseInfo.reddit_comments.length - 1 && (
                                <Divider />
                              )}
                            </React.Fragment>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  )}
              </Box>
            )}

            {insight && (
              <Box
                sx={{ display: "flex", flexDirection: "column", gap: 3, mt: 4 }}
              >
                <Card>
                  <CardContent>
                    <Typography
                      variant="h5"
                      gutterBottom
                      color="primary"
                      sx={{ fontWeight: 600 }}
                    >
                      Course Analysis
                    </Typography>
                    <Box
                      sx={{
                        "& p": {
                          margin: 0,
                          lineHeight: 1.8,
                        },
                        "& strong": {
                          color: "primary.main",
                          fontWeight: 600,
                        },
                      }}
                    >
                      <ReactMarkdown>{insight.summary}</ReactMarkdown>
                    </Box>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent>
                    <Typography
                      variant="h5"
                      gutterBottom
                      color="primary"
                      sx={{ fontWeight: 600 }}
                    >
                      Prerequisites Analysis
                    </Typography>
                    <Box
                      sx={{
                        "& p": {
                          margin: 0,
                          lineHeight: 1.8,
                        },
                        "& strong": {
                          color: "primary.main",
                          fontWeight: 600,
                        },
                      }}
                    >
                      <ReactMarkdown>
                        {insight.prerequisites_analysis}
                      </ReactMarkdown>
                    </Box>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent>
                    <Typography
                      variant="h5"
                      gutterBottom
                      color="primary"
                      sx={{ fontWeight: 600 }}
                    >
                      Difficulty Assessment
                    </Typography>
                    <Box
                      sx={{
                        "& p": {
                          margin: 0,
                          lineHeight: 1.8,
                        },
                        "& strong": {
                          color: "primary.main",
                          fontWeight: 600,
                        },
                      }}
                    >
                      <ReactMarkdown>
                        {insight.difficulty_assessment}
                      </ReactMarkdown>
                    </Box>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent>
                    <Typography
                      variant="h5"
                      gutterBottom
                      color="primary"
                      sx={{ fontWeight: 600 }}
                    >
                      Recommendations
                    </Typography>
                    <List>
                      {insight.recommendations.map((rec, index) => (
                        <ListItem key={index}>
                          <ListItemText
                            primary={
                              <Box
                                sx={{
                                  "& p": {
                                    margin: 0,
                                    lineHeight: 1.8,
                                  },
                                  "& strong": {
                                    color: "primary.main",
                                    fontWeight: 600,
                                  },
                                }}
                              >
                                <ReactMarkdown>{rec}</ReactMarkdown>
                              </Box>
                            }
                            sx={{
                              "& .MuiListItemText-primary": {
                                fontFamily: "'Roboto Mono', monospace",
                              },
                            }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              </Box>
            )}
          </Box>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
