"use client";
import styles from "./page.module.css";
import {
  Box,
  Text,
  Heading,
  Spinner,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  StatGroup,
  Image,
  Spacer,
  Divider,
  Flex,
} from "@chakra-ui/react";
import useSWR from "swr";
import ReactWordcloud from "react-wordcloud";
import { ResponsiveBar } from "@nivo/bar";

// @ts-ignore
const fetcher = (...args: any[]) => fetch(...args).then((res) => res.json());

interface AuthorFreqDict {
  channel_id: string;
  channel_title: string;
  count: number;
}

const MyBarChart = ({
  data,
  indexby,
}: {
  data: AuthorFreqDict[];
  indexby: string;
}) => {
  return (
    <div style={{ height: "400px" }}>
      <ResponsiveBar
        // @ts-ignore
        data={data}
        keys={["count"]}
        indexBy={indexby}
        margin={{ top: 50, right: 130, bottom: 50, left: 60 }}
        padding={0.3}
        valueScale={{ type: "linear" }}
        indexScale={{ type: "band", round: true }}
        colors={{ scheme: "nivo" }}
        borderColor={{ from: "color", modifiers: [["darker", 1.6]] }}
        axisTop={null}
        axisRight={null}
        axisBottom={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: "channel title",
          legendPosition: "middle",
          legendOffset: 32,
        }}
        axisLeft={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: "count",
          legendPosition: "middle",
          legendOffset: -40,
        }}
        labelSkipWidth={12}
        labelSkipHeight={12}
        labelTextColor={{ from: "color", modifiers: [["darker", 1.6]] }}
        legends={[
          {
            dataFrom: "keys",
            anchor: "bottom-right",
            direction: "row",
            justify: false,
            translateX: 120,
            translateY: 0,
            itemsSpacing: 2,
            itemWidth: 100,
            itemHeight: 20,
            itemDirection: "left-to-right",
            itemOpacity: 0.85,
            symbolSize: 20,
            effects: [
              {
                on: "hover",
                style: {
                  itemOpacity: 1,
                },
              },
            ],
          },
        ]}
        animate={true}
        // motionStiffness={90}
        // motionDamping={15}
      />
    </div>
  );
};

export default function Home() {
  const { data, isLoading, error } = useSWR(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/video-metrics`,
    fetcher
  );
  if (isLoading)
    return (
      <Box p={8}>
        <Spinner colorScheme="black" size="xl" />
      </Box>
    );
  if (error)
    return (
      <Box p={8}>
        <Heading>Error loading Metrics</Heading>
      </Box>
    );
  console.log(data);
  const proc_freqs = data.author_frequency.filter(
    (freq: AuthorFreqDict) => freq.count > 1
  );
  console.log(data.comment_author_frequency);
  return (
    <Box m={4}>
      <Box mx="auto" my={2}>
        <Flex alignItems="center">
          <Heading p={2} as="h1" size="xl">
            Data Analysis
          </Heading>
          <Spacer />
        </Flex>
        <Divider />
        <Box>
          <StatGroup rounded="lg" p={8} m={4}>
            <Stat>
              <StatLabel>Videos</StatLabel>
              <StatNumber>{data.video_count}</StatNumber>
            </Stat>

            <Stat>
              <StatLabel>Vax Videos</StatLabel>
              <StatNumber>{data.vax_video_count}</StatNumber>
            </Stat>
            <Stat>
              <StatLabel>Comment Count</StatLabel>
              <StatNumber>{data.comment_count}</StatNumber>
            </Stat>
          </StatGroup>
          <StatGroup rounded="lg" p={8} m={4}>
            <Stat>
              <StatLabel>Avg Comments per vid</StatLabel>
              <StatNumber>{data.avg_vax_video_comments}</StatNumber>
            </Stat>
            <Stat>
              <StatLabel>Avg top comment length</StatLabel>
              <StatNumber>{data.avg_top_comment_length}</StatNumber>
            </Stat>
            <Stat>
              <StatLabel>Avg Child Comments</StatLabel>
              <StatNumber>{data.avg_child_comments}</StatNumber>
            </Stat>
          </StatGroup>
        </Box>
        <Box>
          <Heading size="md">Vaccine Videos Title Word Frequencies</Heading>
          <ReactWordcloud words={data.title_word_frequency} />
        </Box>
        <Box>
          <Heading size="md">Vaccine Videos Tag Word Frequencies</Heading>
          <ReactWordcloud words={data.tag_word_frequency} />
        </Box>
        <Box>
          <Heading size="md">Comment words and frequencies</Heading>
          <ReactWordcloud words={data.comment_word_frequency} />
        </Box>
        <Box>
          <Heading size="md">Video Channel Title and Count</Heading>
          <MyBarChart indexby="channel_title" data={proc_freqs} />
        </Box>
        <Box>
          <Heading size="md">Comment Author Ids and Count</Heading>
          <MyBarChart
            indexby="author_name"
            data={data.comment_author_frequency}
          />
        </Box>
      </Box>
    </Box>
  );
}
