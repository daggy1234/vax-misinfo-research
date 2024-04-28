"use client";

import {
  Box,
  Spinner,
  Heading,
  Spacer,
  Flex,
  Button,
  Input,
  Text,
  Avatar,
  Badge,
  Textarea,
} from "@chakra-ui/react";
import Link from "next/link";
import { useState, useEffect } from "react";
import useInfiniteScroll from "react-infinite-scroll-hook";
import useSWR from "swr";
import { FaLongArrowAltLeft } from "react-icons/fa";
// @ts-ignore
const fetcher = (...args: any[]) => fetch(...args).then((res) => res.json());

const CommentPage = ({ params }: { params: { video_id: string } }) => {
  const { video_id } = params;
  const {
    data: viddata,
    isLoading: vidisLoading,
    error: viderror,
  } = useSWR(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/fetch-video?video_id=${video_id}`,
    fetcher
  );
  const { data, isLoading, error } = useSWR(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/top-comments?video_id=${video_id}`,
    fetcher
  );
  const [sliceEnd, setSliceEnd] = useState(50);
  const [sentryRef] = useInfiniteScroll({
    loading: isLoading,
    hasNextPage: data ? data.data.length > sliceEnd : false,
    disabled: error,
    onLoadMore: () => setSliceEnd((old) => old + 50),
  });
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState([]);

  const handleSearch = (event: any) => {
    setSearchTerm(event.target.value);
  };

  useEffect(() => {
    if (data) {
      const results = data.data.filter((comment: any) =>
        comment.text.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setSearchResults(results);
    }
  }, [searchTerm, data]);

  if (isLoading || vidisLoading)
    return (
      <Box p={8}>
        <Spinner colorScheme="black" size="xl" />
      </Box>
    );
  if (error || viderror)
    return (
      <Box p={8}>
        <Heading>Error loading videos</Heading>
      </Box>
    );

  console.log(viddata);
  return (
    <Box p={4} m={4}>
      <Link href={`https://youtube.com/watch?v=${video_id}`}>
        <Heading
          _hover={{
            textDecoration: "underline",
            color: "blue.400",
          }}>
          {viddata.data.title}
        </Heading>
      </Link>
      <Flex m={2}>
        <Link href={`https://youtube.com/channel/${viddata.data.channel_id}`}>
          <Text color="blue.400">
            <strong>Channel:</strong> {viddata.data.channel_title}
          </Text>
        </Link>
        <Spacer />
        <Badge colorScheme={viddata.data.manual ? "green" : "yellow"}>
          {viddata.data.manual ? "Manual" : "Auto"}
        </Badge>
      </Flex>
      <Flex>
        <Text>
          <strong>Tags:</strong> {viddata.data.tags}
        </Text>
      </Flex>
      <Text>
        <strong>Description:</strong>
      </Text>
      <Textarea isDisabled value={viddata.data.description} />
      <Flex m={2}>
        <Text fontSize="large" fontWeight={"bold"}>
          Comments:
        </Text>
        <Spacer />
        <Link href="/">
          <Button leftIcon={<FaLongArrowAltLeft />} size="lg">
            Back
          </Button>
        </Link>
      </Flex>
      <Input
        placeholder="Search comments"
        value={searchTerm}
        onChange={handleSearch}
      />
      <Box>
        {searchResults.slice(0, sliceEnd).map((comment: any) => (
          <Box
            m={2}
            key={comment.id}
            p={2}
            border="1px solid black"
            borderRadius="md">
            <Flex alignItems="center">
              <Avatar
                mr={2}
                src={comment.author_image}
                name={comment.author_name}
              />
              <Text size="md">{comment.text}</Text>
            </Flex>
          </Box>
        ))}
        <div ref={sentryRef} />
      </Box>
    </Box>
  );
};

export default CommentPage;
