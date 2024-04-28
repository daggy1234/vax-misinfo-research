"use client";
import styles from "./page.module.css";
import {
  Box,
  Text,
  Heading,
  Spinner,
  Image,
  Spacer,
  SimpleGrid,
  Select,
  Button,
  filter,
  Switch,
  Divider,
  Flex,
} from "@chakra-ui/react";
import useSWR from "swr";
import { useState } from "react";
import { FaYoutube, FaExternalLinkAlt } from "react-icons/fa";
import Link from "next/link";
import { useEffect } from "react";

// @ts-ignore
const fetcher = (...args: any[]) => fetch(...args).then((res) => res.json());

export default function Home() {
  const [FilterManual, setFilterManual] = useState(false);
  const [descSort, descSetSort] = useState(true);
  const [sortMethod, SetSort] = useState(0);
  const [sortedData, SetSortedData] = useState([]);
  const { data, isLoading, error, mutate } = useSWR(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/vax-videos?desc_sort=${descSort}`,
    fetcher
  );

  useEffect(() => {
    if (data) {
      let proc_data = data.data.map((video: any) => {
        return { ...video, parsed_date: new Date(video.published_at) };
      });

      proc_data = data.data.filter((video: any) => {
        if (FilterManual) {
          return video.manual;
        } else {
          return !video.manual;
        }
      });
      console.log(sortMethod);
      console.log(proc_data);

      proc_data = proc_data.sort((a: any, b: any) => {
        if (sortMethod === 1) {
          return b.parsed_date - a.parsed_date;
        } else if (sortMethod === 2) {
          return b.count - a.count;
        } else {
          return b.parsed_date - a.parsed_date;
        }
      });

      SetSortedData(proc_data);
    }
  }, [data, FilterManual, sortMethod, descSort]);

  if (isLoading)
    return (
      <Box p={8}>
        <Spinner colorScheme="black" size="xl" />
      </Box>
    );
  if (error)
    return (
      <Box p={8}>
        <Heading>Error loading videos</Heading>
      </Box>
    );

  return (
    <Box m={4}>
      <Box mx="auto" my={2}>
        <Flex alignItems="center">
          <Heading p={2} as="h1" size="xl">
            Videos
          </Heading>
          <Spacer />
          <Select
            mr={2}
            maxW="sm"
            value={sortMethod}
            onChange={(e) => {
              if (Number(e.target.value) === 0) {
                descSetSort(true);
              }
              SetSort(Number(e.target.value));
            }}>
            <option value={0}>Newest</option>
            <option value={1}>Oldest</option>
            <option value={2}>Most Comments</option>
          </Select>
          <Text>Only Manual?</Text>
          <Switch
            ml={2}
            isChecked={FilterManual}
            onChange={() => setFilterManual(!FilterManual)}
          />
        </Flex>
        <Divider />
        <Box>
          <SimpleGrid column={{ base: 1, md: 2, lg: 3, xl: 4 }} spacing={3}>
            {sortedData.map((video: any) => {
              return (
                <Box
                  border="1px solid black"
                  m={2}
                  rounded="md"
                  p={4}
                  key={video.id}>
                  <Flex>
                    <Image
                      w={200}
                      src={video.thumbnail_url}
                      alt={video.title}
                    />
                    <Flex direction="column">
                      <Heading ml={2} isTruncated as="h2" size="lg">
                        {video.title}
                      </Heading>
                      <Text ml={2} fontSize="sm">
                        {video.channel_title}
                      </Text>
                      <Text ml={2} fontSize="sm">
                        Comments: {video.count}
                      </Text>
                      <Flex>
                        <Link
                          href={`https://youtube.com/watch?v=${video.video_id}`}>
                          <Button
                            leftIcon={<FaYoutube />}
                            colorScheme="red"
                            m={2}>
                            Video
                          </Button>
                        </Link>
                        <Link href={`/comments/${video.video_id}`}>
                          <Button leftIcon={<FaExternalLinkAlt />} m={2}>
                            Comments
                          </Button>
                        </Link>
                      </Flex>
                    </Flex>
                  </Flex>
                </Box>
              );
            })}
          </SimpleGrid>
        </Box>
      </Box>
    </Box>
  );
}
